# Makefile for SliTaz Bugs.
#

PACKAGE="tazbug"
PREFIX?=/usr
DESTDIR?=
WEB?=/var/www
VAR?=/var/lib/slitaz
LINGUAS?=de el es fr ja pl pt_BR ru vi zh_CN

all: msgfmt

# i18n

pot:
	xgettext -o po/tazbug.pot -L Shell --package-name="SliTaz Bugs" \
		./web/bugs.cgi \
		./web/plugins/dashboard/dashboard.cgi \
		./web/plugins/mybugs/mybugs.cgi \
		./web/plugins/packages/packages.cgi \
		./web/plugins/users/users.cgi 
	xgettext -o po/cli/tazbug-cli.pot -L Shell --package-name="Tazbug cli" \
		./tazbug

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/$$l.po po/$(PACKAGE).pot; \
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		echo "Compiling $$l mo file..."; \
		mkdir -p po/mo/$$l/LC_MESSAGES; \
		msgfmt -o po/mo/$$l/LC_MESSAGES/$(PACKAGE).mo po/$$l.po; \
	done;

# Client install only. Server part is not packaged

install:
	install -m 0777 -d $(DESTDIR)$(PREFIX)/bin
	install -m 0777 -d $(DESTDIR)$(PREFIX)/share/applications
	install -m 0755 tazbug $(DESTDIR)$(PREFIX)/bin
	install -m 0644 data/tazbug.desktop \
		$(DESTDIR)$(PREFIX)/share/applications

# On SliTaz vhost: make install-web WEB=/home/slitaz/www

install-web:
	install -m 0700 -d $(DESTDIR)$(VAR)/people
	install -m 0700 -d $(DESTDIR)$(VAR)/auth
	install -m 0777 -d $(DESTDIR)$(WEB)/bugs
	# authfile
	touch $(DESTDIR)$(VAR)/auth/people
	chmod 0600 $(DESTDIR)$(VAR)/auth/people
	# admin users
	touch $(DESTDIR)$(VAR)/auth/admin
	chmod 0600 $(DESTDIR)$(VAR)/auth/people
	cp -a web/* $(DESTDIR)$(WEB)/bugs
	cp README $(DESTDIR)$(WEB)/bugs
	chown -R www.www $(DESTDIR)$(VAR)/*
	chown -R www.www $(DESTDIR)$(WEB)/bugs/bug
	# i18n
	install -m 0755 -d $(DESTDIR)$(PREFIX)/share/locale
	cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale

# Uninstall client

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/tazbug*
	rm -f $(DESTDIR)$(PREFIX)/share/applications/tazbug*
	rm -f $(DESTDIR)$(PREFIX)/etc/slitaz/tazbug.conf

# Clean source

clean:
	rm -rf po/mo
	rm -f po/*~
