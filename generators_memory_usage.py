from memory_profiler import profile

MAX_NUMBER_OF_ITEMS = 5_000_000


@profile
def main_list():
    arr = list(range(MAX_NUMBER_OF_ITEMS))

    arr_2 = [i for i in arr if i % 2]

    arr_3 = [i for i in arr_2 if i % 3]

    arr_filtered = [i for i in arr_3 if i != 30]

    print("main_list:", len(arr_filtered))


@profile
def main_gen():
    arr = range(MAX_NUMBER_OF_ITEMS)

    arr_2 = (i for i in arr if i % 2)

    arr_3 = (i for i in arr_2 if i % 3)

    arr_filtered = (i for i in arr_3 if i != 30)

    print("main_gen:", len(list(arr_filtered)))


main_gen()
