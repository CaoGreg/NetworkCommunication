count = 10
toto = ["1", "2", "3"]
while count > 0:
    print(count)
    for tos in toto:
        print(tos)
        if tos == "2" and count == 8:
            break
    else:
        count = count - 1
        continue
    break
else:
    print("time oud")
print("End while")