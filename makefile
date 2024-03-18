#!/usr/bin/make -f
#
# Makefile for LoROM template
# Copyright 2014-2015 Damian Yerrick
#
# Copying and distribution of this file, with or without
# modification, are permitted in any medium without royalty
# provided the copyright notice and this notice are preserved.
# This file is offered as-is, without any warranty.
#
title = helloworld
version = 0.01

define \n


endef

objlist = \
	main snikku periods
	
WLAPATH := ../wla_dx
ASZ80 := $(WLAPATH)/wla-z80
LDZ80 := $(WLAPATH)/wlalink
CFLAGSZ80 := -d -S
objdir := obj/sms
srcdir := src
imgdir := tilesets
musdir := music

ifndef SMSEMU
SMSEMU := ../../Emulicious/Emulicious.exe
endif

ifdef COMSPEC
PY := python.exe
else
PY :=
endif

wincwd := $(shell pwd | sed -e "s'/'\\\\\\\\'g")

# .PHONY means these targets aren't actual filenames
.PHONY: all run dist clean

run: $(title).sms
	$(SMSEMU) $<
	
all: $(title).sms

clean:
	-rm $(objdir)/*.o $(objdir)/linkfile $(objdir)/*.tab
	-rm $(srcdir)/periods.z80 $(srcdir)/testsongtick.z80
	
dist: zip
zip: $(title)-$(version).zip
$(title)-$(version).zip: zip.in all README.md $(objdir)/index.txt
	$(PY) tools/zipup.py $< $(title)-$(version) -o $@
	-advzip -z3 $@
	
# Build zip.in from the list of files in the Git tree
zip.in:
	git ls-files | grep -e "^[^.]" > $@
	echo zip.in >> $@
	echo $(title).sms >> $@
	
$(objdir)/index.txt: makefile
	echo "Files produced by build tools go here. (This file's existence forces the unzip tool to create this folder.)" > $@

objlisto = $(foreach o,$(objlist),$(objdir)/$(o).o)

$(title).sms: $(objdir)/linkfile
	$(LDZ80) $(CFLAGSZ80) -v $(objdir)/linkfile $(title).sms

$(objdir)/linkfile: $(objlisto)
	@printf "[objects]\n" > $@
	@printf $(addsuffix "\n",$^) >> $@

$(objdir)/%.o: $(srcdir)/%.z80
	$(ASZ80) -i -v -o $@ $<
	
#replace with palperiod if your game is for PAL region
$(srcdir)/periods.z80: tools/makenotetable.py
	$(PY) $< period $@
	
$(srcdir)/testsongtick.z80: $(musdir)/NaceTest.bin
	$(PY) tools/furnace2z80.py $< $@ TestSongTick
	
# Files that depend on extra included files
$(srcdir)/main.z80: \
	$(srcdir)/periods.z80 $(srcdir)/testsongtick.z80
