from re import U


uss = open('ussers.txt', 'r')
ussers = uss.readlines()
ff = ussers[1][:-1]
print(ff[:-1])
print(ussers[2])
print(len(ff))