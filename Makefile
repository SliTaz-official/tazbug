# Makefile for SliTaz Bugs.
#

PACKAGE="tazbug"
PREFIX?=/usr
DESTDIR?=
WEB?=/var/www
VAR?=/var/lib/slitaz
LINGUAS?=ru

all:

# i18n

pot:
	xgettext -o po/tazbug.pot -L Shell --package-name="SliTaz Bugs" \
		./tazbug ./tazbug-box ./web/bugs.cgi

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/$$l.po po/$(PACKAGE).pot; \
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		echo "Compiling $$l mo file..."; \
		mkdir -p po/mo/$$l/LC_MESSAGES; \
		msgfmt -o po/mo/$$l/LC_MESSAGES/pizza.mo po/$$l.po; \
	done;

# Client install only. Server part is not packaged

install:
	install -m 0777 -d $(DESTDIR)/etc/slitaz
	install -m 0777 -d $(DESTDIR)$(PREFIX)/bin
	install -m 0777 -d $(DESTDIR)$(PREFIX)/share/applications
	install -m 0755 tazbug $(DESTDIR)$(PREFIX)/bin
	install -m 0755 tazbug-box $(DESTDIR)$(PREFIX)/bin
	install -m 0644 tazbug.conf $(DESTDIR)/etc/slitaz
	install -m 0644 data/tazbug.desktop \
		$(DESTDIR)$(PREFIX)/share/applications

# On SliTaz vhost: make install-server WEB=/home/slitaz/www

install-server:
	install -m 0777 -d $(DESTDIR)/etc/slitaz
	install -m 0700 -d $(DESTDIR)$(VAR)/people
	install -m 0700 -d $(DESTDIR)$(VAR)/auth
	install -m 0777 -d $(DESTDIR)$(PREFIX)/share/doc/tazbug
	install -m 0777 -d $(DESTDIR)$(WEB)/bugs
	install -m 0644 tazbug.conf $(DESTDIR)/etc/slitaz
	touch $(DESTDIR)$(VAR)/auth/people
	chmod 0600 $(DESTDIR)$(VAR)/auth/people
	cp -a web/* $(DESTDIR)$(WEB)/bugs
	cp README $(DESTDIR)$(PREFIX)/share/doc/tazbug
	chown -R www.www $(DESTDIR)$(VAR)/*
	chown -R www.www $(DESTDIR)$(WEB)/bugs/bug

# Uninstall client

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/tazbug*
	rm -f $(DESTDIR)$(PREFIX)/share/applications/tazbug*
	rm -f $(DESTDIR)$(PREFIX)/etc/slitaz/tazbug.conf
