"""Various methods to process lists of things."""


def split_list_to_equal_buckets(list_to_split, desired_buckets=10):
    """Split a given list into a list of equally sized buckets."""
    if list_to_split is None or len(list_to_split) < 1:
        raise ValueError('Given list to reduce was empty')

    if desired_buckets > len(list_to_split):
        desired_buckets = len(list_to_split)

    f_length_of_list = float(len(list_to_split))
    f_desired_buckets = float(desired_buckets)
    f_blocksize = f_length_of_list / f_desired_buckets
    i_blocksize = int(f_blocksize)

    f_bucketrest = f_length_of_list - (i_blocksize * desired_buckets)

    if f_bucketrest != 0:
        f_add_one_interval = f_desired_buckets / f_bucketrest
        f_insertion_point = f_add_one_interval

    subsets = []
    for _ in range(0, desired_buckets):
        subset = []
        subsets.append(subset)

    p_subset = 0
    p_count = 0
    t_count = 0
    iterator = iter(list_to_split)

    if f_bucketrest != 0:
        subsets[p_subset].append(float(iterator.__next__()))
        t_count += 1
    while t_count < len(list_to_split):
        subsets[p_subset].append(float(iterator.__next__()))
        p_count += 1
        t_count += 1
        if p_count == i_blocksize:
            if f_bucketrest != 0 and p_subset >= f_insertion_point:
                subsets[p_subset].append(
                    float(iterator.__next__()))
                p_count += 1
                t_count += 1
                f_insertion_point += f_add_one_interval
            p_subset += 1
            p_count = 0

    return subsets


def reduce_list(list_to_reduce, desired_elements=10):
    """Reduce list to a number of elements, averaging over blocks."""
    subsets = split_list_to_equal_buckets(list_to_reduce, desired_elements)

    def avg(x): return sum(x) / len(x)

    out_list = []
    for subset in subsets:
        value = avg(subset)
        out_list.append(value)

    return out_list


def intersect(list_a, list_b):
    """Intersect the two given lists."""
    if list_a is None or list_b is None:
        raise ValueError('Lists cannot be none')
    return list(set(list_a) & set(list_b))


def sub_strings_in_list(sr_patterns, list_in):
    """Take a list of strings and apply given patterns to all elements."""
    from re import sub
    list_out = []
    for el in list_in:
        for sr_pattern in sr_patterns:
            el = sub(sr_pattern[0], sr_pattern[1], el)
        list_out.append(el)
    return list_out
