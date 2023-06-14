from lxml import etree
from collections import defaultdict


class Parser():
   """This class contains different parsers to parse files with various extensions."""
  
   def __init__(self):
       pass


   def appendValue(self, dict_: dict, key_: str, value_: str) -> dict:
       """
       This function appends a given value to a dictionary if it is not none.


       Args:
           dict_: A dictionary for appending a given value
           key_: A string representing the key
           value_: A sring value to be added


       Returns:
           dict_: A dictionary with appended value
       """


       if value_:
           if key_ in dict_:
               dict_[key_].append(value_)
           else:
               dict_[key_] = [value_]
      
       return dict_


   def parse_xml(self, xmlFile: str) -> dict:
       """
       This function parses an input xml file to extract metadata


       Args:
           xmlFile: An input xml file
          
       Returns:
           meta_dict: A dictionary that contains extracted metadata          
       """ 
      
       # Parse the XML file
       tree = etree.parse(xmlFile)
       root = tree.getroot()


       # Create a dictionary to hold the metadata extracted from the file
       meta_dict = {}
      
       # Find and get the elements from the file and append them to metadata dictionary
       for title in root.xpath('//title'):
           title_ = title.get('title')
           year = title.find('year').text
          
           self.appendValue(meta_dict, "title", title_)
           self.appendValue(meta_dict, "year", year)
          
       for author in title.xpath('./author_name'):
           author = author.get('name')
           self.appendValue(meta_dict, "author", author)
          
       return meta_dict


   def parse_plain(self, txtFile: str) -> dict:
       """
       This function parses an input txt file to extract metadata
      
       Args:
           txtFile: An input text file
          
       Returns:
           meta_dict: A dictionary that contains extracted metadata  
       """  


       # Create a dictionary to hold the metadata extracted from the file
       meta_dict = {}
      
       # Read the author name(s) from the file and append to metadata dictionary
       with open(txtFile, "r") as file:
           for line in file:
               if "Author Name:" in line:
                   author = line.split("Author Name:")[1].strip()
                   self.appendValue(meta_dict, "author", author)


       return meta_dict
