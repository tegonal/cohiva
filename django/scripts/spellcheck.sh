#!/bin/bash
for F in website/templates/*.html ; do
  aspell --mode=html --lang=de_CH -c $F
done
