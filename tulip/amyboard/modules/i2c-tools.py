import amyboard

print("Scanning I2C bus...")
i2c = amyboard.get_i2c()
devices = i2c.scan()

if not devices:
    print("No I2C devices found - check wiring, power, and pull-ups")
else:
    print(f"Found {len(devices)} device(s):")
    for addr in devices:
        print(f"  0x{addr:02X}")
