import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def txt_to_xml(txt_path, output_folder):
    with open(txt_path, 'r') as file:
        lines = file.readlines()

    parking_type = lines[0].strip()
    angle = lines[1].strip()
    objects = []

    for line in lines[2:]:
        data = line.strip().split('\t')
        occupancy = data[0]
        name = parking_type + occupancy + angle
        coords = data[1:]

        objects.append((name, coords))

    xml_root = ET.Element("annotation")
    ET.SubElement(xml_root, "filename").text = os.path.basename(txt_path).replace('.txt', '.jpg')
    ET.SubElement(xml_root, "folder").text = "data/train"
    ET.SubElement(xml_root, "object_num").text = str(len(objects))

    for name, coords in objects:
        xml_object = ET.SubElement(xml_root, "object")
        ET.SubElement(xml_object, "name").text = name
        xml_quad = ET.SubElement(xml_object, "quad")

        for i in range(4):
            ET.SubElement(xml_quad, f"x{i + 1}").text = coords[i * 2]
            ET.SubElement(xml_quad, f"y{i + 1}").text = coords[i * 2 + 1]

    xml_string = ET.tostring(xml_root, encoding="utf-8", method="xml")
    xml_pretty = minidom.parseString(xml_string).toprettyxml(indent="  ")

    output_xml_path = os.path.join(output_folder, os.path.basename(txt_path).replace('.txt', '.xml'))

    with open(output_xml_path, 'w') as file:
        file.write(xml_pretty)

def main():
    input_folder = "data/train/label"
    output_folder = "data/train/xml"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            txt_path = os.path.join(input_folder, filename)
            txt_to_xml(txt_path, output_folder)

if __name__ == "__main__":
    main()
