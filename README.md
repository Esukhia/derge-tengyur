<p align="center">
  <span>English</span> |
  <a href="https://github.com/Esukhia/derge-tengyur/blob/master/README.bo.md">བོད་ཡིག</a> |
  <a href="https://github.com/Esukhia/derge-tengyur/blob/master/README.zh-tw.md">繁體中文</a>
</p>

# Digital Derge Tengyur

Working repository for the digital Derge Tengyur prepared by Esukhia and Barom Theksum Choling. This repository aims at being an annotated faithful copy of the Derge edition of the Tengyur. Each file of the `derge-tengyur-tags` directory is the input of a volume of the Derge Tengyur, with page and line indication. See the [catalog by the Tohoku University](https://www.tbrc.org/#!rid=W1PD95677) to find a specific text. The indexes indicated in this catalog are also indicated in the files.

## Downloads

- [Volumes, plain text format, version 2019-05](https://github.com/Esukhia/derge-tengyur/releases/download/1905/deten_vol_txt_v1905.zip)
- [Volumes, Kumara-jiva tsv format, version 2019-05](https://github.com/Esukhia/derge-tengyur/releases/download/1905/deten_vol_kjtsv_v1905.zip)


## Format

The texts contain the following structural markup at beginning of lines:

* **[1b]** is _[Page and folio markers]_
* **[1b.1]** is _[Page and folio markers.line number]_

We follow the page numbers indicated in the original, this means that sometimes the page numbers go back to 1a (ex: vol. 31 after p. 256). Pages numbers that appear twice in a row are indicated with an `x`, example in volume 102: `[355xa]`.

They also contain a few error suggestions noted as example. It is far from an exhausted list of the issues found in the original, the staff was actually discouraged to add these.

* **(X,Y)** is _(potential error, correction suggestion)_ , example: `མཁའ་ལ་(མི་,མེ་)ཏོག་དམར་པོ་`

* **[X]** signals obvious errors or highly suspicious spellings (ex: `མཎྜལ་ཐིག་[ལ་]ལྔ་པ་ལ།`), or un-transcribable characters
* **#** signals an unreadable graphical unit
* **{DX}** signals the beginning of the text with Tohoku catalog number **X**. We use the following conventions:
  * when a text is missing from the Tohoku catalog, we indicate it with the preceding number followed by **a**, ex: **D7**, **D7a**, **D8**, following the [rKTs](https://www.istb.univie.ac.at/kanjur/rktsneu/sub/index.php) convention.

TODO: format of notes insertion.

## Encoding

### Unicode

The files are UTF8 with no BOM, using LF end of lines, in [NFD](http://unicode.org/reports/tr15/). The following representations are used:

 - `\u0F68\u0F7C\u0F7E` (`ཨོཾ`) is used instead of `\u0F00` (`ༀ`)
 - `\u0F62\u0FB1` (`རྱ`) is used instead of `\u0F6A\u0FB1` (`ཪྱ`)
 - `\u0F62\u0F99` (`རྙ`) is used instead of `\u0F6A\u0F99` (`ཪྙ`)
 - `\u0F62\u0FB3` (`རླ`) is used instead of `\u0F6A\u0FB3` (`ཪླ`)
 - `\u0F6A\u0FBB` (`ཪྻ`) is used for the most common form instead of `\u0F62\u0FBB` (`རྻ`)

Some characters in volume 197 (starting p. 361a) denote the long / short syllables, example:

![ssktlenmarkers](https://user-images.githubusercontent.com/17675331/45107718-106e0f00-b16d-11e8-9759-9f169bce3c48.png)
![ssktlenmarkers2](https://user-images.githubusercontent.com/17675331/45107711-0cda8800-b16d-11e8-8f85-19728bf41123.png)

These characters have no Tibetan version in Unicode, so we use the following characters which we believe are the Sanskrit equivalents:
 - `ऽ` for heavy (`ऽं` when with anusvara)
 - `।` for light (`।ं` when with anusvara)

### Punctuation

The end of lines sometimes are preceded by a space character (when they end with a shad) so that the result of appending all the lines content is correct.

We apply the following normalization without keeping the original in parenthesis:
 - `༄༅། །` at beginning of pages are removed, unless they also denote the beginning of a text (this also applies to the first pages of volumes)
 - `༑` are replaced by `།`

We keep the original punctuation in parenthesis (see above) but normalize the following:
 - `༄༅། །` are added at beginning of texts when they're missing
 - `ག། །།` instead of `ག།། །།`, or with any character conforming `[གཀཤ][ོེིུ]?` instead of ག
 - a tshek is inserted between characters conforming `ང[ོེིུ]?` and `།`

## Page numbering issues

These page numbering issues appear in the original scans and have been kept:
- vol. 209 goes from page 87 to page 89, and from page 89 to page 91

## Export works

In order to export each work in a different file, run:

        cd .scripts/
        python3 export_works.py

The output will be in `scripts/export`.

The volume in which the work is found(the filename) is added on two occasions:
at the beginning of each work and when there is a volume change within a single work.

To get the raw text with no markup, run `python3 export_works.py --clean-content true`.


# Feedback

The files are on Github hoping they'll improve, don't hesitate to [report issues](https://github.com/Esukhia/derge-tengyur/issues) or even open a pull request!

# How to cite

Use the following statemnent:
    
     ཚུལ་ཁྲིམས་རིན་ཆེན། [1697-1774], བཀའ་འགྱུར་སྡེ་དགེ་པར་མ།, various etexts combined and further proofread by Esukhia on behalf of Barom Theksum Choling, 2014-2018, https://github.com/Esukhia/derge-tengyur

# License

This work is a mechanical reproduction of a Public Domain work, and as such is also in the Public Domain.
