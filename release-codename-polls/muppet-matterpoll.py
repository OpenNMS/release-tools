#!/usr/bin/env python3

# Release codename poll generator – works with Matterpoll
#
# After each release, increment version and remove the just-used codename from
# candidate_names in this script so that it will not appear in the next
# release's poll.

product="Meridian"
version="2023.1.1"
criterion="Muppet"

candidate_names = [
    "Abby Cadabby",
    "Animal",
    "Beaker",
    "Bert",
    "Big Bird",
    "Cookie Monster",
    "Count von Count",
    "Dr. Bunsen Honeydew",
    "Dr. Teeth",
    "Elmo",
    "Ernie",
    "Floyd Pepper",
    "Fozzie Bear",
    "Gonzo",
    "Grover",
    "Guy Smiley",
    "Janice",
    "Julia",
    "Kermit the Frog",
    "Lips",
    "Miss Piggy",
    "Mr. Snuffleupagus",
    "Murray Monster",
    "Oscar the Grouch",
    "Pepe the King Prawn",
    "Rizzo the Rat",
    "Roosevelt Franklin",
    "Rosita",
    "Rowlf the Dog",
    "Sam Eagle",
    "Scooter",
    "Sherlock Hemlock",
    "Statler",
    "The Martians",
    "The Swedish Chef",
    "The Two-Headed Monster",
    "Waldorf",
    "Walter",
    "Zoot"
]

poll_string = '/poll "First round: Which {} should be the codename for {} {}? Please vote for exactly one." '.format(criterion, product, version)
for candidate in candidate_names:
    poll_string += '"{}" '.format(candidate)

print(poll_string)
