'''
Useful functions to be used by my other classes
'''

def combine_dicts(dict_list):
    combined_dict = {}
    for k in dict_list[0]:
        combined_dict[k] = tuple(d[k] for d in dict_list)
    return combined_dict
