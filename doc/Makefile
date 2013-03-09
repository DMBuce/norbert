mandir        = /usr/local/share/man
man1dir       = $(mandir)/man1
man2dir       = $(mandir)/man2
man3dir       = $(mandir)/man3
man4dir       = $(mandir)/man4
man5dir       = $(mandir)/man5
man6dir       = $(mandir)/man6
man7dir       = $(mandir)/man7
man8dir       = $(mandir)/man8
man9dir       = $(mandir)/man9
MAN1PAGES := norbert.1
MAN5PAGES := norbert.5
MANPAGES  := $(MAN1PAGES) $(MAN5PAGES)
MAN1PAGES_INSTALL := $(MAN1PAGES:doc/%=$(DESTDIR)$(man1dir)/%)
MAN5PAGES_INSTALL := $(MAN5PAGES:doc/%=$(DESTDIR)$(man5dir)/%)
TXTFILES  := norbert.1.txt norbert.5.txt
HTMLPAGES := $(TXTFILES:.txt=.html)

#TGT_INSTALL := $(TGT_INSTALL) doc-install
#CLEAN       := $(MANPAGES) $(HTMLPAGES)
#DIST        := $(DIST) doc
#
#DISTCLEAN := $(DISTCLEAN) \
#             $(MANPAGES) \
#             $(HTMLPAGES)

INSTALLDIRS := $(INSTALLDIRS) $(DESTDIR)$(man1dir) $(DESTDIR)$(man5dir)

UNINSTALL := $(UNINSTALL) \
             $(MAN1PAGES_INSTALL) \
             $(MAN5PAGES_INSTALL)

ASCIIDOC_OPTS=-f asciidoc.conf \
	-a BUGREPORT='https://github.com/DMBuce/norbert/issues' \
	-a URL='http://dmbuce.github.com/norbert' \
	-a REPO='https://github.com/DMBuce/norbert'

# default target
.PHONY: all
all: doc



# install man pages

$(DESTDIR)$(man1dir)/%: doc/%
	- $(INSTALL_DATA) $< $@

$(DESTDIR)$(man5dir)/%: doc/%
	- $(INSTALL_DATA) $< $@



# compile man pages with asciidoc

%.1: %.1.txt
	a2x --no-xmllint -d manpage -f manpage --asciidoc-opts="${ASCIIDOC_OPTS} -d manpage" $<

%.5: %.5.txt
	a2x --no-xmllint -d manpage -f manpage --asciidoc-opts="${ASCIIDOC_OPTS} -d manpage" $<



# compile html-format man pages with asciidoc

%.1.html: %.1.txt
	asciidoc ${ASCIIDOC_OPTS} -a toc -a icons -a max-width=960px -d manpage $<
                                                                            
%.5.html: %.5.txt                                                   
	asciidoc ${ASCIIDOC_OPTS} -a toc -a icons -a max-width=960px -d manpage $<



# compile html documentation with asciidoc

%.html: %.txt
	asciidoc ${ASCIIDOC_OPTS} -a toc -a icons -a max-width=960px $<



# phony targets

.PHONY: doc-install doc html clean

doc-install: $(MAN1PAGES_INSTALL) $(MAN5PAGES_INSTALL)

doc: $(MANPAGES)

html: $(HTMLPAGES)

clean:
	rm -f $(MANPAGES) $(HTMLPAGES)


# vim: set ft=make:
