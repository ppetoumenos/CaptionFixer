# CaptionFixer
Simple tool for fixing auto-generated captions in the VTT format using the original script

## Usage

`./fix_captions <captionfile.vtt> <scriptfile.txt>`

The modified file is saved in captionfile.new.vtt

## Functionality

The tool is simple. At its core it just:

1. does Sequence Alignment on the texts of the vtt and txt files
2. uses the alignment to replace the captions text with the script text, while keeping timestamps unchanged

The tool also does some simple substitutions, hardcoded in _COMMON_SUBS in fix_captions.py. It also treats common homonyms as identical for sequence alignment purposes.

## Output

If the original and modified captions for each timestamp are similar enough, CaptionFixer takes a leap of faith and replaces the original caption.

Otherwise, both the original and modified captions are printed, prefixed with "---" and "+++" respectively.

Finally, if the original caption contained text that does not match the script, e.g., because the speaker went off script, the modified caption will keep that text but now ounded by "*". For example:

Script:

`This is what makes C++ better that all other languages.`

Original caption:

`This is what makes c plus plus better than all other languages assuming of course that you use a very narrow definition of better`

Modified caption:

`This is what makes C++ better that all other languages. *assuming of course that you use a very narrow definition of better*`
