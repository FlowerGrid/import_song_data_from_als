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
    file_path = 'MultiTrack.als'
    song_title, extension = os.path.splitext(file_path)


    if extension == '.als':
        xml_path = convert_als_to_xml(file_path, song_title)
        file_path = xml_path

    xml_tree = ET.parse(file_path)
    xml_root = xml_tree.getroot()

    # Gather title
    # Gather key
    # Gather Markers
    # Gather time signature and meter changes
    # Gather Tempo and Tempo changes

def convert_als_to_xml(als_path, song_title):
    xml_path = song_title + '.xml'

    with gzip.open(als_path, 'rb') as f_in:
        xml_data = f_in.read()

    with open(xml_path, 'wb') as f_out:
        f_out.write(xml_data)

    return xml_path


def gather():
    ...

if __name__ == '__main__':
    main()