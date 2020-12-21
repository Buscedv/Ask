import random

def int(start, end, count=1):
    """ 
    A function to return 'n' random integers between a given range 'Start' to 'End'
        parameters: 
        start - start of the range
        end - end of the range (inclusive)
        count(optional) - number of random integers to return, default value is 1
        Note: count <= end-start
    """

    if end-start < count:
        raise ValueError("Count of the integers should not be greater than the input range !")
    if count>1:
        return random.sample(range(start, end), count)
    else:
        return random.randint(start, end)


def float(start, end, count=1, decimals=16):
    """ 
    A function to return 'n' random floats between a given range 'Start' to 'End'
        parameters: 
        start - start of the range
        end - end of the range (inclusive)
        count(optional) - number of random floats to return, default value is 1
        decimals(optional) - number of digits after the decimal, default value is 16
    """

    if count>1:
        unique_floats = set()
        for x in range(1, count+1):
            n = round(random.uniform(start, end), decimals)
            while n in unique_floats:
                n = round(random.uniform(start, end), decimals)
            unique_floats.add(n)
        unique_floats = list(unique_floats)
        return unique_floats
    else:
        return round(random.uniform(start, end), decimals)


def item(iterable, weights=None,count=1):
    """
    A function to return 'n' sample items from an iterable object
    parameters:
        iterable - the object from which sample is to be taken
        weight(optional) - (integer list) the weight to be given to individual element, default is 'equal'
        count(optional) - number of samples to be selected, default is 1
    """
    return random.choices(iterable, weights=weights ,k=count)

