#!/usr/bin/env python3

# Release codename poll generator – works with Matterpoll
#
# After each release, increment version and remove the just-used codename from
# candidate_names in this script so that it will not appear in the next
# release's poll.

product="Meridian"
version="2023.1.11"
criterion="Muppet"

candidate_names = [
    "Abby Cadabby",
    "Animal",
    "Bert",
    "Big Bird",
    "Elmo",
    "Ernie",
    "Floyd Pepper",
    "Fozzie Bear",
    "Grover",
    "Guy Smiley",
    "Janice",
    "Julia",
    "Lips",
    "Miss Piggy",
    "Murray Monster",
    "Oscar the Grouch",
    "Pepe the King Prawn",
    "Roosevelt Franklin",
    "Rosita",
    "Rowlf the Dog",
    "Sam Eagle",
    "Scooter",
    "Sherlock Hemlock",
    "Statler",
    "The Martians",
    "The Two-Headed Monster",
    "Waldorf",
    "Walter"
]

poll_string = '/poll "First round: Which {} should be the codename for {} {}? Please vote for exactly one." '.format(criterion, product, version)
for candidate in candidate_names:
    poll_string += '"{}" '.format(candidate)

print(poll_string)
