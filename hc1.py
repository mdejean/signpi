#!/usr/bin/python3

"""
Handles the format read by the HC-1 HUB75 LED matrix controller
"""

import struct

header = (
    ">12s"  # COLOR_01.PRG
    + "4B"  # Unknown, changes
    # +0x10
    + "4B"  # Unknown, static 0x61
    + "2x2B"  # 0x3864 or 0x3094?
    + "B3x"  # 0x51
    + "I"  # 0
    # +0x20
    + "xHx"  # 0x1800 (number of pixels, 192*32), 0
    + "4H"  # c020 1000 c002 0000 - relates to display configuration?
    + "3xB"  # Display brightness: 0 = maximum, 4 = minimum
    # +0x30
    + "16B"  # 0-15
    # +0x40
    + "I"  # 0x00101010
    + "428x"  # 0
    # +0x1F0
    + "16B"  # 00 00 00 10 10 01 01 00 00 00 00 00 00 01 0A 00
    # +0x200
    + "16H"  # 0x0000 0x0010 .. 0x00F0
    # +0x220
    + "1504x"  # 0
    # +0x800
)

page_header = (
    ">"
    + "HH"  # 09010A10
    + "HH"  # 06 00 C0 00
    + "H"  # 20 01 00 00
    + "xHx"  # Number of frames
    + "H"  # 0
    + "3xB"  # 0x00000014
)

frame_header = (
    ">"
    + "B?2x"  # Frame time in false: 1/100 s true: 1/10 s
    + "H2x"  # offset of frame data start from 0x1000
    + "I"  # 0
    + "I"  # 0
)


def pack_header(brightness):
    return struct.pack(
        header,
        b"COLOR_01.PRG",
        0x17,
        0x03,
        0x18,
        0x0C,
        0x27,
        0x0D,
        0x00,
        0x61,
        0x38,
        0x64,
        0x51,
        0,
        0x1800,
        0xC020,
        0x1000,
        0xC002,
        0x0000,
        brightness,
        *list(range(16)),
        0x101010,
        0x00,
        0x00,
        0x00,
        0x10,
        0x10,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x01,
        0x0A,
        0x00,
        *list(range(0, 0x100, 0x10))
    )


def pack_frames(frames, frame_secs):
    assert len(frames) == len(frame_secs)

    def sec_to_frames(frames, frame_secs):
        for frame, frame_sec in zip(frames, frame_secs):
            frame_time = frame_sec / 0.005
            while frame_time > 255:
                yield b"", 255
                frame_time -= 255
            yield frame, round(frame_time)

    n_expanded_frames = sum(1 for _ in sec_to_frames(frames, frame_secs))
    ret = struct.pack(
        page_header, 0x0901, 0x0A10, 0x0600, 0xC000, 0x2001, n_expanded_frames, 0, 0x14
    )
    start = struct.calcsize(page_header) + n_expanded_frames * struct.calcsize(
        frame_header
    )
    for frame, frame_time in sec_to_frames(frames, frame_secs):
        long_frame = False
        if frame_time > 255:
            frame_time = frame_time // 10
            long_frame = True
        ret += struct.pack(frame_header, frame_time, long_frame, start, 0, 0)
        start += len(frame)
    for frame in frames:
        ret += frame
    return ret


def generate_prg(brightness, frames, frame_times):
    return pack_header(brightness) * 2 + pack_frames(frames, frame_times)
