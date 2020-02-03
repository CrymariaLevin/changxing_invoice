from decimal import Decimal

aa = Decimal('5.00001').quantize(Decimal('0.00'))
print(type(aa))
a = str(aa)
print(type(float(a)))

print(type(a))
print(a)