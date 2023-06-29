import inspect
import json
import sys
import pyDaRUS

def collect_metadata_attributes(json_data):

    attributes = {}

    def traverse_json(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "metadata":
                    for attr, attr_value in value.items():
                        if attr in attributes:
                            attributes[attr].append(attr_value)
                        else:
                            attributes[attr] = [attr_value]
                traverse_json(value)
        elif isinstance(obj, list):
            for item in obj:
                traverse_json(item)

    traverse_json(json_data)
    return attributes


def get_objects(library, depth =2):

    obj_dict = {}

    def traverse(obj, path, current_depth):

        if current_depth > depth:
            return

        if inspect.ismodule(obj):
            for name, item in inspect.getmembers(obj):
                if inspect.isclass(item) or inspect.ismodule(item):
                    new_path = f"{path}.{name}" if path else name
                    obj_dict[new_path] = {}
                    traverse(item, new_path, current_depth+1)
        elif inspect.isclass(obj):
            for name, attr in obj.__dict__.items():
                if not name.startswith('__'):
                    new_path = f"{path}.{name}" if path else name
                    obj_dict[path][new_path] = str(attr)

    traverse(library, "", 0)
    return obj_dict

    #objects = {}
    
    #print(inspect.getmembers(library))
    #for name, obj in inspect.getmembers(library):
    #    if inspect.isclass(obj) or inspect.isfunction(obj):
    #        objects[name] = obj

    #return objects
    
    #object_dictionary = {}
    #sys.setrecursionlimit(3000)  # Set the recursion depth limit to a higher value

    #def traverse_module(module, module_path):
    #    for name, obj in inspect.getmembers(module):
    #        if inspect.isclass(obj):
    #            class_path = f"{module_path}.{name}"
    #            object_dictionary[class_path] = get_class_attributes(obj)
    #            traverse_class(obj, class_path)

    #def traverse_class(cls, class_path):
    #    for name, obj in inspect.getmembers(cls):
    #        if inspect.isclass(obj):
    #            nested_class_path = f"{class_path}.{name}"
    #            object_dictionary[nested_class_path] = get_class_attributes(obj)
    #            traverse_class(obj, nested_class_path)

    #def get_class_attributes(cls):
    #    attributes = []
    #    for name, value in inspect.getmembers(cls):
    #        if not name.startswith('_'):
    #            attributes.append(name)
    #    return attributes

    #def traverse_library(obj, path):
    #    for name, value in inspect.getmembers(obj):
    #        if inspect.isclass(value):
    #            class_path = f"{path}.{name}"
    #            object_dictionary[class_path] = [attr for attr, _ in inspect.getmembers(value) if not attr.startswith('_')]
    #            traverse_library(value, class_path)

    #for name, module in inspect.getmembers(library):
    #    if inspect.ismodule(module):
    #        traverse_class(module, name)

    #return object_dictionary


def print_tree(dictionary, indent=0):
    for key, value in dictionary.items():
        print("  " * indent + key)
        if isinstance(value, dict):
            print_tree(value, indent + 1)
        else:
            if not isinstance(value, (list, tuple)):
                value = [value]
            for attr in value:
                print("  " * (indent + 1) + str(attr))



# Call the function to get the objects in the library
library_objects = get_objects(pyDaRUS)

# Print the objects in the library
print("easyDataverse objects")
print_tree(library_objects)


# Read JSON data from a file
file_path = '/home/sarbani/darus_data_harvester/harvester/harvester_output.json'
with open(file_path) as file:
    json_data = json.load(file)

# Call the function to collect metadata attributes
metadata_attributes = collect_metadata_attributes(json_data)

# Print the collected attributes
print("collected attributes")
print_tree(metadata_attributes)