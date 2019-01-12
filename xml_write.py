# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 16:09:23 2018

@author: ud
"""

from xml.dom.minidom import getDOMImplementation

##module to create xml file. Input given are id number and file name
def create_xml_file(number,file_name):
    impl = getDOMImplementation()

    newdoc = impl.createDocument(None, "Message", None)
    top_element = newdoc.documentElement
    header =newdoc.createElement("Header")

    value  =newdoc.createElement("Verb")
    value_text = newdoc.createTextNode('poll')
    value.appendChild(value_text)

    noun = newdoc.createElement("Noun")
    noun_text =newdoc.createTextNode('Load')
    noun.appendChild(noun_text)

    id_no = newdoc.createElement("id")
    id_no_text =newdoc.createTextNode(number)
    id_no.appendChild(id_no_text)

    header.appendChild(value)
    header.appendChild(noun)
    header.appendChild(id_no)
    top_element.appendChild(header)
    #text = newdoc.createTextNode('Some textual content.')
    #top_element.appendChild(text)
    newdoc.writexml( open(file_name, 'w'),
               indent="  ",
               addindent="  ",
               newl='\n')
 
    newdoc.unlink()

if '__name__' == '__main__':
        pass