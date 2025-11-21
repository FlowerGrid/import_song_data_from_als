"""
- Convert .als to .xml
- Parse XML to gather song data
- Song title doesn't appear to be available
- Song key may not be available
- Section markers store in locator tags
- Marker text in locator tags name = section marker, time = beat number
    - There are other things in locator tags that don't look like section markers
- Time signature in ArrangerAutomation > Events > TimeSignature
    - numerator = beats per measure
    - denominator = beat value
    - time = beat number
        - this is where time signature changes will be marked
- Tempo might be in MasterTrack > DeviceChain > Mixer > Tempo > Manual
"""

import gzip
import os
import sys
import xml.etree.ElementTree as ET

def gather_song_data_from_file(file_path):

    song_title, extension = os.path.splitext(file_path)

    if extension == '.als':
        xml_path = convert_als_to_xml(file_path, song_title)
        file_path = xml_path

    try:
        xml_tree = ET.parse(file_path)
        xml_root = xml_tree.getroot()

        # Gather title
        title = gather_title(xml_root)
        # Gather time signature and meter changes
        time_sig, denom = gather_time_signature(xml_root)
        # Gather Markers
        markers = gather_markers(xml_root, int(denom))
        # Gather Tempo and Tempo changes
        tempo = gather_tempo(xml_root)

        return {"title": title, 
                "markers": markers,
                "time_sig": time_sig,
                "tempo": tempo}
    except Exception as e:
        sys.exit('Could not Parse File')


def convert_als_to_xml(als_path, song_title):
    xml_path = song_title + '.xml'

    with gzip.open(als_path, 'rb') as f_in:
        xml_data = f_in.read()

    with open(xml_path, 'wb') as f_out:
        f_out.write(xml_data)

    return xml_path


def gather_title(xml_root):
    # title = xml_root.find('.//TrackName')
    for elem in xml_root.iter('TrackName'):
        # print(elem)
        ...


def gather_markers(xml_root, denom):
    markers = []
    markers_string = ''
    print(denom)

    locators = list(xml_root.iter("Locator"))
    for locator in locators:
        name = locator.find('Name')
        marker = name.get('Value')
        beat_loc = locator.find('Time')
        beat_num = int(beat_loc.get('Value'))
        markers.append((beat_num, marker))
    
    sorted_markers = sorted(markers)

    ending_idx = 0
    beat = 0
    for i, m in enumerate(sorted_markers):
        print(f"{m[1]} {m[0]}")
        # idx - title - start time - order - label - duration - end time - fade time - status - actions
        if denom == 4:
            beat = m[0]
        elif denom == 8:
            beat = m[0]/2
        else:
            sys.exit('Beat mapping error')

        markers_string += f'{i + 1}\t{m[1]}\tstart time\t{i+1}\t{m[1]}\t{beat}\tend time\tfade time\tstatus\tactions'

        if m[1].lower() == 'ending':
            break

        markers_string += os.linesep
        
    return markers_string


def gather_time_signature(xml_root):
    meter_string = ''

    time_sigs = list(xml_root.iter('RemoteableTimeSignature'))
    print(time_sigs)
    if not time_sigs:
        denom = 4
        return '4/4 (0.0000)', denom
    
    sigs_list = []
    for i, time_sig in enumerate(time_sigs):
        numer = time_sig.find('Numerator').get('Value')
        denom = time_sig.find('Denominator').get('Value')
        beat_loc = int(time_sig.find('Time').get('Value'))

        sigs_list.append((beat_loc, f'{numer}/{denom}'))

    for i, sig in enumerate(sorted(sigs_list)):
        meter_string += f'{sig[1]} ({sig[0]}.0000)'
        if i < (len(time_sigs) - 1):
            meter_string += os.linesep

    return meter_string, denom


def gather_tempo(xml_root):
    tempo_tag = xml_root.find('.//Tempo')
    events_tags = list(tempo_tag.iter('Events'))
    if events_tags:
        tempo_events = []
        for tag in events_tags:
            float_event = tag.find('FloatEvent')
            tempo = float_event.get('Value')
            beat_loc = float(float_event.get('Time'))
            tempo_events.append((beat_loc, tempo))

        tempo_events = sorted(tempo_events)

        # Return first tempo event for now, we can return all of them later
        return f'{tempo_events[0][1]}.00'
    
    manual_tag = tempo_tag.find('Manual')
    if manual_tag is not None:
        tempo = f"{manual_tag.get('Value')}.00"
        return tempo


if __name__ == '__main__':
    file_path = 'Gratitude.als'
    gather_song_data_from_file(file_path)