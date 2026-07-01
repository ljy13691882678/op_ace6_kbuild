import sys

target = 'kernel_platform/common/arch/arm64/kernel/cpuinfo.c'
print(f"Reading {target}...")

with open(target) as f:
    content = f.read()

pos = content.find('static int c_show(struct seq_file *m, void *v)')
if pos < 0:
    pos = content.find('int c_show(struct seq_file *m')
if pos < 0:
    print("ERROR: c_show not found!")
    sys.exit(1)

print(f"Found at {pos}")

# 找函数结束
brace_count = 0
end = -1
for i in range(pos, len(content)):
    if content[i] == '{':
        brace_count += 1
    elif content[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            end = i + 1
            break

print(f"Function length: {end - pos}")

new_func = """static int c_show(struct seq_file *m, void *v)
{
    int i;
    static const u32 fake_midr[] = {
        (0x48U << 24) | (0x1U << 20) | (0xfU << 16) | (0xd0eU << 4) | 0x0U,
        (0x48U << 24) | (0x2U << 20) | (0xfU << 16) | (0xd0fU << 4) | 0x0U,
        (0x48U << 24) | (0x2U << 20) | (0xfU << 16) | (0xd0fU << 4) | 0x0U,
        (0x48U << 24) | (0x2U << 20) | (0xfU << 16) | (0xd0fU << 4) | 0x0U,
        (0x48U << 24) | (0x3U << 20) | (0xfU << 16) | (0xd10U << 4) | 0x0U,
        (0x48U << 24) | (0x3U << 20) | (0xfU << 16) | (0xd10U << 4) | 0x0U,
        (0x48U << 24) | (0x3U << 20) | (0xfU << 16) | (0xd10U << 4) | 0x0U,
        (0x48U << 24) | (0x3U << 20) | (0xfU << 16) | (0xd10U << 4) | 0x0U,
    };
    for_each_online_cpu(i) {
        u32 midr = (i < ARRAY_SIZE(fake_midr)) ? fake_midr[i] : fake_midr[ARRAY_SIZE(fake_midr)-1];
        seq_printf(m, "processor\\t: %d\\n", i);
        seq_printf(m, "Processor\\t: AArch64 Processor rev %d (aarch64)\\n", MIDR_REVISION(midr));
        seq_printf(m, "BogoMIPS\\t: 26.00\\n");
        seq_puts(m, "Features\\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp\\n");
        seq_printf(m, "CPU implementer\\t: 0x%02x\\n", MIDR_IMPLEMENTOR(midr));
        seq_printf(m, "CPU architecture: 8\\n");
        seq_printf(m, "CPU variant\\t: 0x%x\\n", MIDR_VARIANT(midr));
        seq_printf(m, "CPU part\\t: 0x%03x\\n", MIDR_PARTNUM(midr));
        seq_printf(m, "CPU revision\\t: %d\\n\\n", MIDR_REVISION(midr));
    }
    seq_printf(m, "Hardware\\t: HiSilicon Kirin 9020\\n");
    return 0;
}"""

new_content = content[:pos] + new_func + content[end:]
with open(target, 'w') as f:
    f.write(new_content)

with open(target) as f:
    check = f.read()
if 'fake_midr' in check and 'Kirin 9020' in check:
    print("VERIFIED!")
else:
    print("FAILED!")
    sys.exit(1)
