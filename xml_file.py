# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import xml.dom.minidom
import xml_write





def main():
    #use the parse function to load and parse on xml file
    doc= xml.dom.minidom.parse("get.xml")
    print(doc.nodeName)
    print(doc.firstChild.nodeName)
    #get the list of html tag from document and print each one
    #tag_name = doc.getElementsByTagName("type")
    #tag_name =tag_name[0].firstChild.nodeValue.encode('utf-8')
    #print(type(tag_name))
    #print(tag_name)
    tag_name = doc.getElementsByTagName("Verb")
    tag_name = tag_name[0].firstChild.nodeValue.encode('utf-8')
    if tag_name.strip() == 'poll':
                            print("It is update response")
                            noun = doc.getElementsByTagName("Noun")
                            noun = noun[0].firstChild.nodeValue.encode('utf-8')
                            if noun.strip() == 'Load':
                                id_load     = doc.getElementsByTagName("id")
                                id_load     = id_load[0].firstChild.nodeValue.encode('utf-8')
                                id_load     = id_load.strip()
                                print(id_load)
                                type_load   = doc.getElementsByTagName("type")
                                type_load   = type_load[0].firstChild.nodeValue.encode('utf-8')
                                type_load   = type_load.strip()
                                print(type_load)
                                value_load  = doc.getElementsByTagName("value")
                                value_load  = value_load[0].firstChild.nodeValue.encode('utf-8')
                                value_load  = value_load.strip()
                                print(value_load)
                                #Load_list[Load_list.index(i)] = Load_struct(ip_address = addr[0] , id = id_load , type =type_load, value =value_load)
                                #os.remove("poll.xml")
    xml_write.create_xml_file(str(5000) , 'data.xml')
                                
if __name__ == "__main__":
    main()