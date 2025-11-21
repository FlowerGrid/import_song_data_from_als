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
import shutil
import xml.etree.ElementTree as ET

def main():
    file_path = 'Gratitude.als'
    song_title, extension = os.path.splitext(file_path)


    if extension == '.als':
        xml_path = convert_als_to_xml(file_path, song_title)
        file_path = xml_path

    xml_tree = ET.parse(file_path)
    xml_root = xml_tree.getroot()

    print(xml_root.get('MajorVersion'))

    # Gather title
    title = gather_title(xml_root)
    # Gather Markers
    markers = gather_markers(xml_root)
    # Gather time signature and meter changes
    time_sig = gather_time_signature(xml_root)
    # Gather Tempo and Tempo changes
    tempo = gather_tempo(xml_root)
    print(tempo)

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
        print(elem)


def gather_markers(xml_root):
    markers = []
    markers_string = ''

    locators = list(xml_root.iter("Locator"))
    for locator in locators:
        name = locator.find('Name')
        marker = name.get('Value')
        beat_loc = locator.find('Time')
        beat_num = f"{beat_loc.get('Value')}.00"
        markers.append((beat_num, marker))
    
    sorted_markers = sorted(markers)

    ending_idx = 0
    for i, m in enumerate(sorted_markers):
        # idx - title - start time - order - label - duration - end time - fade time - status - actions
        markers_string += f'{i + 1}\t{m[1]}\tstart time\t{i+1}\t{m[1]}\t{m[0]}\tend time\tfade time\tstatus\tactions'

        if m[1].lower() == 'ending':
            break

        markers_string += os.linesep
        
    print(markers_string)
    return markers_string


def gather_time_signature(xml_root):
    meter_string = ''

    time_sigs = list(xml_root.iter('RemoteableTimeSignature'))
    for i, time_sig in enumerate(time_sigs):
        numer = time_sig.find('Numerator').get('Value')
        denom = time_sig.find('Denominator').get('Value')
        beat_loc = f"{time_sig.find('Time').get('Value')}.0000"

        meter_string += f'{numer}/{denom} ({beat_loc})'
        if i < (len(time_sigs) - 1):
            meter_string += os.linesep

    print(meter_string)


def gather_tempo(xml_root):
    tempo_tag = xml_root.find('.//Tempo')
    events_tags = list(tempo_tag.iter('Events'))
    if events_tags:
        tempo_events = []
        for tag in events_tags:
            float_event = tag.find('FloatEvent')
            tempo = float_event.get('Value')
            beat_loc = float_event.get('Time')
            tempo_events.append((beat_loc, tempo))

        tempo_events = sorted(tempo_events)
        print('here')

        # Return first tempo event for now, we can return all of them later
        return tempo_events[0][1] + '.00'
    
    manual_tag = tempo_tag.find('Manual')
    if manual_tag is not None:
        tempo = f"{manual_tag.get('Value')}.00"
        return tempo


if __name__ == '__main__':
    main()