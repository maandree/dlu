PREFIX = /usr
BINDIR = $(PREFIX)/bin
DATADIR = $(PREFIX)/share
MANDIR = $(DATADIR)/man
MAN1DIR = $(MANDIR)/man1
LICENSEDIR = $(DATADIR)/licenses

COMMAND = dlu
PKGNAME = dlu

all:

install: install-base install-doc
install-base: install-cmd install-copyright
install-doc: install-man
install-copyright: install-license

install-cmd:
	mkdir -p -- "$(DESTDIR)$(BINDIR)"
	install -m755 -- dlu.py "$(DESTDIR)$(BINDIR)/$(COMMAND)"

install-man:
	mkdir -p -- "$(DESTDIR)$(MAN1DIR)"
	install -m644 -- dlu.1 "$(DESTDIR)$(MAN1DIR)/$(COMMAND).1"

install-license:
	mkdir -p -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	install -m644 -- LICENSE "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/LICENSE"

uninstall:
	-rm -- "$(DESTDIR)$(BINDIR)/$(COMMAND)"
	-rmdir -- "$(DESTDIR)$(BINDIR)"
	-rm -- "$(DESTDIR)$(MAN1DIR)/$(COMMAND).1"
	-rmdir -- "$(DESTDIR)$(MAN1DIR)"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/LICENSE"
	-rmdir -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"

clean:

.PHONY: all clean
