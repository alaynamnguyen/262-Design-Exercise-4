# Recursive function for object to dict
def object_to_dict_recursive(obj):
    """Recursively converts objects to dictionaries."""
    if hasattr(obj, "__dict__"):
        return {key: object_to_dict_recursive(value) for key, value in vars(obj).items()}
    return obj

# Recursive function for dict to object
def dict_to_object_recursive(dct, cls):
    """Converts a dictionary back to an object of type cls."""
    obj = cls.__new__(cls)  # Create an empty instance
    for key, value in dct.items():
        setattr(obj, key, dict_to_object_recursive(value, globals().get(cls.__name__, object)) if isinstance(value, dict) else value)
    return obj

def protobuf_list_to_object(proto_list, target_class, key_field):
    """
    Converts a list of protobuf objects into a dictionary of custom Python objects.

    Parameters:
    ----------
    proto_list : list of protobuf objects
        The list of protobuf objects received from the server.
    target_class : class
        The Python class to instantiate (e.g., Message, User).
    key_field : str
        The field name to use as the dictionary key (e.g., "mid" for messages, "uid" for users).

    Returns:
    -------
    dict
        A dictionary where the key is the specified field value and the value is an instance of target_class.
    """
    print("Calling protobuf_list_to_object")
    obj_dict = {}

    for proto_obj in proto_list:
        # Convert Protobuf object fields into a dictionary
        obj_data = {field.name: getattr(proto_obj, field.name) for field in proto_obj.DESCRIPTOR.fields}
        
        # Create an instance of the target class
        obj_instance = target_class(**obj_data)

        # Use the specified field as the dictionary key
        obj_dict[getattr(proto_obj, key_field)] = obj_instance

    return obj_dict

def object_to_protobuf_list(obj_dict, proto_class):
    """
    Converts a dictionary of custom Python objects into a list of corresponding protobuf objects.

    Parameters:
    ----------
    obj_dict : dict
        Dictionary where the key is an identifier, and the value is a Python object (e.g., Message, User).
    proto_class : class
        The protobuf class to instantiate (e.g., chat_pb2.MessageData, user_pb2.UserData).

    Returns:
    -------
    list
        A list of protobuf objects corresponding to the input dictionary values.
    """
    proto_list = []

    for obj in obj_dict.values():
        # Convert Python object attributes into a dictionary
        obj_data = obj.__dict__

        # Create a protobuf object using the extracted data
        proto_obj = proto_class(**obj_data)

        proto_list.append(proto_obj)

    return proto_list
