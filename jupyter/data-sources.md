# Data sources

# German news RSS feeds

- <http://randyzwitch.com/creating-stacked-bar-chart-seaborn/>

```
http://www.spiegel.de/index.rss
http://www.tagesschau.de/xml/rss2
http://www.faz.net/rss/aktuell
http://www.stern.de/feed/standard/all/
http://rssfeed.sueddeutsche.de/c/795/f/449002/index.rss
http://www.bild.de/rss-feeds/rss-16725492,feed=home.bild.html
http://www.taz.de/rss.xml
https://www.welt.de/feeds/latest.rss
http://rss.focus.de/politik/
http://www.n-tv.de/rss
http://newsfeed.zeit.de/index
http://www.handelsblatt.com/contentexport/feed/top-themen/
```

# Obfuscated code

```
# filter out spiegel plus content for now
# (deobfuscation will be applied soon)
# if (
#     search('www\.spiegel\.de', r.text) and
#     search('<p[ ]+class=\"obfuscated\"[ ]*>', r.text)
# ):
    # b_util.log(
    #     'WARN: \'{}\' skipped because of missing deobfuscation of spiegel-plus content'.format(url))
    # b_util.update_progressbar()
    # return
```

- from test

```
# ------------
# without obfuscated text, don't do anything
# dat_in = '\n'.join(
#     b_iotools.read_file_to_list(self.get_res_path('html-in.txt')))
# dat_out = b_parse.deobfuscate_spiegel_plus_content(dat_in)
# self.assertEqual(dat_in, dat_out)
# with obfuscated text, translate text
# dat_in = '\n'.join(
#     b_iotools.read_file_to_list(self.get_res_path('spiegel-plus.txt')))
# dat_out = b_parse.deobfuscate_spiegel_plus_content(dat_in)
```
