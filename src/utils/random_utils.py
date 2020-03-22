from numpy.random import choice


def random_choice_from_dict(choice_dict, weight_name):
    """
    Assumes the given dictionary has elements with weight_name as key and a float as value.
    Returns the value of the randomly selected element.
    """
    choices = list(choice_dict)
    chances = []
    for choice_name in choice_dict:
        chances.append(choice_dict[choice_name].get(weight_name))
    decimal_chances = [chance / sum(chances) for chance in chances]
    key = choice(choices, p=decimal_chances)
    value = choice_dict[key]
    return value
