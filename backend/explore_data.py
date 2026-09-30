import csv
with open("Questions.csv", encoding = "ISO-8859-1") as file:
    reader = csv.reader(file)
    for i, row in enumerate(reader):
        pass
print(f"Read {i + 1} rows successfully with no errors.")