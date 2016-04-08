#!/usr/bin/env python
#
# Copyright 2015,2016 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import random, time, struct
import pmt
from gnuradio import gr, gr_unittest, digital, blocks
from gnuradio.digital import packet_utils

class test_packet_format_fb(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_packet_format_async_default(self):
        ac = packet_utils.default_access_code
        formatter = digital.packet_formatter_default(ac, 0)

        pkt_header = digital.packet_format_async(formatter)
        snk_hdr = blocks.message_debug()
        snk_pld = blocks.message_debug()

        self.tb.msg_connect(pkt_header, 'header', snk_hdr, 'store')
        self.tb.msg_connect(pkt_header, 'payload', snk_pld, 'store')


        send_str = "Hello World"
        send_pmt = pmt.make_u8vector(len(send_str), ord(' '))
        for i in range(len(send_str)):
            pmt.u8vector_set(send_pmt, i, ord(send_str[i]))
        msg = pmt.cons(pmt.PMT_NIL, send_pmt)

        port = pmt.intern("in")
        pkt_header.to_basic_block()._post(port, msg)

        self.tb.start()
        while (snk_hdr.num_messages() < 1) and (snk_pld.num_messages() < 1):
            time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        result_hdr_pmt = pmt.cdr(snk_hdr.get_message(0))
        result_pld_pmt = pmt.cdr(snk_pld.get_message(0))

        result_hdr = pmt.u8vector_elements(result_hdr_pmt)
        result_pld = pmt.u8vector_elements(result_pld_pmt)
        header = "".join([chr(r) for r in result_hdr])
        payload = "".join([chr(r) for r in result_pld])

        access_code = packet_utils.conv_1_0_string_to_packed_binary_string(packet_utils.default_access_code)[0]
        rx_access_code = header[0:len(access_code)]

        length = len(send_str)
        rx_length = struct.unpack_from("!H", header, len(access_code))[0]

        self.assertEqual(access_code, rx_access_code)
        self.assertEqual(length, rx_length)
        self.assertEqual(length, len(payload))
        self.assertEqual(send_str, payload[0:length])


    def test_packet_format_async_counter(self):
        bps = 2
        ac = packet_utils.default_access_code
        formatter = digital.packet_formatter_counter(ac, 0, 2)

        pkt_header = digital.packet_format_async(formatter)
        snk_hdr = blocks.message_debug()
        snk_pld = blocks.message_debug()

        self.tb.msg_connect(pkt_header, 'header', snk_hdr, 'store')
        self.tb.msg_connect(pkt_header, 'payload', snk_pld, 'store')


        send_str = "Hello World" + 1000*"xxx"
        send_pmt = pmt.make_u8vector(len(send_str), ord(' '))
        for i in range(len(send_str)):
            pmt.u8vector_set(send_pmt, i, ord(send_str[i]))
        msg = pmt.cons(pmt.PMT_NIL, send_pmt)

        port = pmt.intern("in")
        pkt_header.to_basic_block()._post(port, msg)

        self.tb.start()
        while (snk_hdr.num_messages() < 1) and (snk_pld.num_messages() < 1):
            time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        result_hdr_pmt = pmt.cdr(snk_hdr.get_message(0))
        result_pld_pmt = pmt.cdr(snk_pld.get_message(0))

        result_hdr = pmt.u8vector_elements(result_hdr_pmt)
        result_pld = pmt.u8vector_elements(result_pld_pmt)
        header = "".join([chr(r) for r in result_hdr])
        payload = "".join([chr(r) for r in result_pld])

        access_code = packet_utils.conv_1_0_string_to_packed_binary_string(packet_utils.default_access_code)[0]
        rx_access_code = header[0:len(access_code)]

        length = len(send_str)
        rx_length = struct.unpack_from("!H", header, len(access_code))[0]
        rx_bps = struct.unpack_from("!H", header, len(access_code)+4)[0]
        rx_counter = struct.unpack_from("!H", header, len(access_code)+6)[0]

        self.assertEqual(access_code, rx_access_code)
        self.assertEqual(length, rx_length)
        self.assertEqual(bps, rx_bps)
        self.assertEqual(0, rx_counter)
        self.assertEqual(length, len(payload))
        self.assertEqual(send_str, payload[0:length])

if __name__ == '__main__':
    gr_unittest.run(test_packet_format_fb, "test_packet_format_fb.xml")
