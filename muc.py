#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import sys
import re
import logging
import getpass
import subprocess
from optparse import OptionParser

import sleekxmpp
import weather
import train
import qa_bot
import morse
import music_163
from simple_cache import SimpleCache

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class MUCBot(sleekxmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will greets those
    who enter the room, and acknowledge any messages
    that mentions the bot's nickname.
    """

    def __init__(self, jid, password, room, nick):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.room = room
        self.nick = nick

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The groupchat_message event is triggered whenever a message
        # stanza is received from any chat room. If you also also
        # register a handler for the 'message' event, MUC messages
        # will be processed by both handlers.
        self.add_event_handler("groupchat_message", self.muc_message)
        self.add_event_handler("message", self.message)

        # The groupchat_presence event is triggered whenever a
        # presence stanza is received from any chat room, including
        # any presences you send yourself. To limit event handling
        # to a single room, use the events muc::room@server::presence,
        # muc::room@server::got_online, or muc::room@server::got_offline.
        self.add_event_handler("muc::%s::got_online" % self.room,
                               self.muc_online)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.get_roster()
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        # If a room password is needed, use:
                                        # password=the_room_password,
                                        wait=True)

    def muc_message(self, msg):
        """
        Process incoming message stanzas from any chat room. Be aware
        that if you also have any handlers for the 'message' event,
        message stanzas may be processed by both handlers, so check
        the 'type' attribute when using a 'message' event handler.

        Whenever the bot's nickname is mentioned, respond to
        the message.

        IMPORTANT: Always check that a message is not from yourself,
                   otherwise you will create an infinite loop responding
                   to your own messages.

        This handler will reply to messages that mention
        the bot's nickname.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['mucnick'] != self.nick and self.nick in msg['body']:
            self.send_message(mto=msg['from'].bare,
                              mbody="I heard that, %s." % msg['mucnick'],
                              mtype='groupchat')

    def muc_online(self, presence):
        """
        Process a presence stanza from a chat room. In this case,
        presences from users that have just come online are
        handled by sending a welcome message that includes
        the user's nickname and role in the room.

        Arguments:
            presence -- The received presence stanza. See the
                        documentation for the Presence stanza
                        to see how else it may be used.
        """
        if presence['muc']['nick'] != self.nick:
            self.send_message(mto=presence['from'].bare,
                              mbody="Hello, %s %s" % (presence['muc']['role'],
                                                      presence['muc']['nick']),
                              mtype='groupchat')

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['type'] in ('chat', 'normal'):
            msg_body = msg['body']
            print("body: %s " % msg_body)
            m = re.match(r'^(\[-\])?(\[(?P<nick>.*)\])?(?P<msg_body>.*)', msg_body)
            if m:
                from_nick = m.groupdict().get('nick')
                if not from_nick:
                    from_nick = msg['from']
                msg_body = m.groupdict().get('msg_body')

                reg_str = r'^[+@\'!](?P<nick>%s|%s|%s):? (?P<msg_body>.*)$' % \
                          (self.nick, u'小二', u'鸡气人')
                p = re.compile(reg_str, re.IGNORECASE)
                m = p.match(msg_body.strip())
                if m:
                    # 默认消息
                    result = u'我是 Lisa 的妹妹，我啥也不会干。:)'
                    msg_body = m.groupdict().get('msg_body')
                    # 翻译
                    if re.search(r'^[a-zA-Z\-]+$', msg_body):
                        result = "%s/html" % run_trans(msg_body).split('\n')[0]
                    # 查快递
                    elif re.search(r'^%s[\w\-]+$' % u'快[递遞]', msg_body):
                        reg_str = r'%s(?P<number>[\w+\-]+)$' % u'快[递遞]'
                        p = re.compile(reg_str, re.IGNORECASE)
                        m = p.match(msg_body.strip())
                        if m:
                            result = run_kuaidi(m.groupdict().get('number'))
                            result = "%s/html" % result.split('\n')[0]
                    # 查天气
                    elif re.search(r'%s' % u'天[气氣]$', msg_body.strip()):
                        reg_str = r'(.*)%s$' % u'天[气氣]'
                        p = re.compile(reg_str, re.IGNORECASE)
                        m = p.match(msg_body.strip())
                        if m:
                            city = m.group(1)
                            result = weather.fetch_weather(city)
                    # 查车次(... 返回详情)
                    elif re.search(r'^%s' % u'[车車]次', msg_body):
                        reg_str = r'^%s(?P<train_num>[\w\-]+)(?P<more>...)?$'\
                                  % u'[车車]次'
                        p = re.compile(reg_str, re.IGNORECASE)
                        m = p.match(msg_body.strip())
                        if m:
                            d = m.groupdict()
                            train_num = d.get('train_num')
                            more = d.get('more')
                            result = train.fetch_train_time(train_num, more)
                    # 莫尔斯码
                    elif re.search(r'^Morse', msg_body, re.IGNORECASE):
                        reg_str = r'^Morse(?P<opt>[<>])(?P<code>[\w\d /.-]+)$'
                        p = re.compile(reg_str, re.IGNORECASE)
                        m = p.match(msg_body)
                        if m:
                            d = m.groupdict()
                            code = d.get('code')
                            option = d.get('opt')
                            if option == '<':
                                if len(code) <= 1024:
                                    result = morse.encode_morse(code)
                                else:
                                    result = u'太长了不能处理。:)'
                            else:
                                # code strip 一下防止空格打头
                                # code 加个空格，确保完整处理
                                code = code.strip()
                                if len(code) <= 4096:
                                    result = morse.decode_morse(code + ' ')
                                else:
                                    result = u'太长了不能处理。:)'
                    else:
                        # 聊天机器人
                        result = qa_bot.qa_request_text(msg_body, from_nick)

                    if result:
                        msg.reply(result).send()
                # 修改消息
                elif re.search(r'^s/(\w+)/(\w+)/?$', msg_body.strip(), re.UNICODE):
                    reg_str = r'^s/(?P<sub>\w+)/(?P<rep>\w+)/?$'
                    p = re.compile(reg_str, re.UNICODE)
                    m = p.match(msg_body.strip())
                    if m:
                        d = m.groupdict()
                        sub_str = u'%s' % d.get('sub')
                        replace_str = u'%s' % d.get('rep')
                        last_message = u'%s' % SimpleCache('last_message', from_nick).get()
                        if last_message:
                            result = re.sub(sub_str, replace_str, last_message)
                            if result != last_message:
                                result = u'[%s] %s' % (from_nick, result)
                                if msg['from'] not in ('water@vim-cn.com/bot',):
                                    msg.reply(result).send()
                # 音乐搜索
                elif re.search(r'^ ?[\'!@]m?163', msg_body, re.IGNORECASE):
                    reg_str = r'^ ?[\'!@](?P<opt>m?163) (?P<query>\w+)$'
                    p = re.compile(reg_str, re.UNICODE)
                    m = p.match(msg_body)
                    if m:
                        d = m.groupdict()
                        opt = d.get('opt')
                        if opt == '163' and msg['from'] in ('offtopic@archlinuxcn.org/bot', 'talk@archlinuxcn.org/bot'):
                            return;

                        query = d.get('query', None)
                        if query is not None:
                            result = music_163.search(query)
                            msg.reply(result).send()
                else:
                    # 缓存群友消息，缓存300s
                    SimpleCache('last_message', from_nick).save(msg_body, 300)


def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    return p.stdout.read()


CFP_COMMAND = "curl -F 'vimcn=<-' https://cfp.vim-cn.com/"


def run_trans(word):
    command = '/usr/local/bin/ydcv.py "%s" | %s' % (word, CFP_COMMAND)
    return run_command(command)


def run_kuaidi(number):
    command = '/usr/local/bin/tracking.py -n %s | %s' % (number, CFP_COMMAND)
    return run_command(command)


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-r", "--room", dest="room",
                    help="MUC room to join")
    optp.add_option("-n", "--nick", dest="nick",
                    help="MUC nickname")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.room is None:
        opts.room = raw_input("MUC room: ")
    if opts.nick is None:
        opts.nick = raw_input("MUC nickname: ")

    # Setup the MUCBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = MUCBot(opts.jid, opts.password, opts.room, opts.nick)
    xmpp.register_plugin('xep_0030')  # Service Discovery
    xmpp.register_plugin('xep_0045')  # Multi-User Chat
    xmpp.register_plugin('xep_0199')  # XMPP Ping
    xmpp.register_plugin('xep_0060')  # PubSub
    xmpp.register_plugin('xep_0004')  # Data Forms

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
