text = "via domen"
input_value = "VIA domencio fontana"

print(len(text), len(input_value), len(input_value.split()))

input_value = " ".join(input_value.split()[:2])
print(
    input_value[:8],
)  # Output: "VIA domencio"
