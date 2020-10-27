import sys
import re

# define delimiters
HARD_DELIMITER_CHARSET = frozenset(u'.'
                                   u'?'
                                   u'!'
                                   u'؟')

SOFT_DELIMITER_CHARSET = frozenset(u','
                                   u';'
                                   u':'
                                   u'،'
                                   u'؛')

# we use a set of quotation marks for the cases where a period comes before the closing quotation "like this."
QUOTATION_MARKS = frozenset(u'"'
                            u"'"
                            u'“'
                            u'”'
                            u'‛'
                            u'’'
                            u'«'
                            u'»'
                            u'‹'
                            u'›')

# define a regular expression that matches EOS symbols with more than 1 occurence
_HARD_DELIMITER_RE = re.compile(u'[^▁]' + u'[' + u''.join(HARD_DELIMITER_CHARSET) + u']+' + '[' + ''.join(QUOTATION_MARKS) + ']?')
# regular expression that matches text up to the last delimiter
_SOFT_DELIMITER_RE = re.compile(u'.*' + u'[' + u''.join(SOFT_DELIMITER_CHARSET) + u']')

# https://github.com/madisonmay/CommonRegex/blob/000473fc5c627a473e277cd66fdf8e451ba080a8/commonregex.py#L9-L10
link = re.compile('(?i)((?:https?://|www\d{0,3}[.])?[a-z0-9.\-]+[.](?:(?:international)|(?:construction)|(?:contractors)|(?:enterprises)|(?:photography)|(?:immobilien)|(?:management)|(?:technology)|(?:directory)|(?:education)|(?:equipment)|(?:institute)|(?:marketing)|(?:solutions)|(?:builders)|(?:clothing)|(?:computer)|(?:democrat)|(?:diamonds)|(?:graphics)|(?:holdings)|(?:lighting)|(?:plumbing)|(?:training)|(?:ventures)|(?:academy)|(?:careers)|(?:company)|(?:domains)|(?:florist)|(?:gallery)|(?:guitars)|(?:holiday)|(?:kitchen)|(?:recipes)|(?:shiksha)|(?:singles)|(?:support)|(?:systems)|(?:agency)|(?:berlin)|(?:camera)|(?:center)|(?:coffee)|(?:estate)|(?:kaufen)|(?:luxury)|(?:monash)|(?:museum)|(?:photos)|(?:repair)|(?:social)|(?:tattoo)|(?:travel)|(?:viajes)|(?:voyage)|(?:build)|(?:cheap)|(?:codes)|(?:dance)|(?:email)|(?:glass)|(?:house)|(?:ninja)|(?:photo)|(?:shoes)|(?:solar)|(?:today)|(?:aero)|(?:arpa)|(?:asia)|(?:bike)|(?:buzz)|(?:camp)|(?:club)|(?:coop)|(?:farm)|(?:gift)|(?:guru)|(?:info)|(?:jobs)|(?:kiwi)|(?:land)|(?:limo)|(?:link)|(?:menu)|(?:mobi)|(?:moda)|(?:name)|(?:pics)|(?:pink)|(?:post)|(?:rich)|(?:ruhr)|(?:sexy)|(?:tips)|(?:wang)|(?:wien)|(?:zone)|(?:biz)|(?:cab)|(?:cat)|(?:ceo)|(?:com)|(?:edu)|(?:gov)|(?:int)|(?:mil)|(?:net)|(?:onl)|(?:org)|(?:pro)|(?:red)|(?:tel)|(?:uno)|(?:xxx)|(?:ac)|(?:ad)|(?:ae)|(?:af)|(?:ag)|(?:ai)|(?:al)|(?:am)|(?:an)|(?:ao)|(?:aq)|(?:ar)|(?:as)|(?:at)|(?:au)|(?:aw)|(?:ax)|(?:az)|(?:ba)|(?:bb)|(?:bd)|(?:be)|(?:bf)|(?:bg)|(?:bh)|(?:bi)|(?:bj)|(?:bm)|(?:bn)|(?:bo)|(?:br)|(?:bs)|(?:bt)|(?:bv)|(?:bw)|(?:by)|(?:bz)|(?:ca)|(?:cc)|(?:cd)|(?:cf)|(?:cg)|(?:ch)|(?:ci)|(?:ck)|(?:cl)|(?:cm)|(?:cn)|(?:co)|(?:cr)|(?:cu)|(?:cv)|(?:cw)|(?:cx)|(?:cy)|(?:cz)|(?:de)|(?:dj)|(?:dk)|(?:dm)|(?:do)|(?:dz)|(?:ec)|(?:ee)|(?:eg)|(?:er)|(?:es)|(?:et)|(?:eu)|(?:fi)|(?:fj)|(?:fk)|(?:fm)|(?:fo)|(?:fr)|(?:ga)|(?:gb)|(?:gd)|(?:ge)|(?:gf)|(?:gg)|(?:gh)|(?:gi)|(?:gl)|(?:gm)|(?:gn)|(?:gp)|(?:gq)|(?:gr)|(?:gs)|(?:gt)|(?:gu)|(?:gw)|(?:gy)|(?:hk)|(?:hm)|(?:hn)|(?:hr)|(?:ht)|(?:hu)|(?:id)|(?:ie)|(?:il)|(?:im)|(?:in)|(?:io)|(?:iq)|(?:ir)|(?:is)|(?:it)|(?:je)|(?:jm)|(?:jo)|(?:jp)|(?:ke)|(?:kg)|(?:kh)|(?:ki)|(?:km)|(?:kn)|(?:kp)|(?:kr)|(?:kw)|(?:ky)|(?:kz)|(?:la)|(?:lb)|(?:lc)|(?:li)|(?:lk)|(?:lr)|(?:ls)|(?:lt)|(?:lu)|(?:lv)|(?:ly)|(?:ma)|(?:mc)|(?:md)|(?:me)|(?:mg)|(?:mh)|(?:mk)|(?:ml)|(?:mm)|(?:mn)|(?:mo)|(?:mp)|(?:mq)|(?:mr)|(?:ms)|(?:mt)|(?:mu)|(?:mv)|(?:mw)|(?:mx)|(?:my)|(?:mz)|(?:na)|(?:nc)|(?:ne)|(?:nf)|(?:ng)|(?:ni)|(?:nl)|(?:no)|(?:np)|(?:nr)|(?:nu)|(?:nz)|(?:om)|(?:pa)|(?:pe)|(?:pf)|(?:pg)|(?:ph)|(?:pk)|(?:pl)|(?:pm)|(?:pn)|(?:pr)|(?:ps)|(?:pt)|(?:pw)|(?:py)|(?:qa)|(?:re)|(?:ro)|(?:rs)|(?:ru)|(?:rw)|(?:sa)|(?:sb)|(?:sc)|(?:sd)|(?:se)|(?:sg)|(?:sh)|(?:si)|(?:sj)|(?:sk)|(?:sl)|(?:sm)|(?:sn)|(?:so)|(?:sr)|(?:st)|(?:su)|(?:sv)|(?:sx)|(?:sy)|(?:sz)|(?:tc)|(?:td)|(?:tf)|(?:tg)|(?:th)|(?:tj)|(?:tk)|(?:tl)|(?:tm)|(?:tn)|(?:to)|(?:tp)|(?:tr)|(?:tt)|(?:tv)|(?:tw)|(?:tz)|(?:ua)|(?:ug)|(?:uk)|(?:us)|(?:uy)|(?:uz)|(?:va)|(?:vc)|(?:ve)|(?:vg)|(?:vi)|(?:vn)|(?:vu)|(?:wf)|(?:ws)|(?:ye)|(?:yt)|(?:za)|(?:zm)|(?:zw))(?:/[^\s()<>]+[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019])?)', re.IGNORECASE)
email = re.compile("([a-z0-9!#$%&'*+\/=?^_`{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)

# for combining regular expressions using pipe symbol later on
_LINK_RE = link.pattern
_EMAIL_RE = email.pattern

# for period in decimal number
_DECIMAL_RE = u'(\d+[.]\d+)'

# derived from ALMOR DB ditributed in camel_tools
# https://raw.githubusercontent.com/CAMeL-Lab/camel_tools/master/camel_tools/calima_star/databases/almor-msa/almor-msa-r13.db
# grep pos:abbrev almor-msa-r13.db | grep -v -e DEFAULT -e DEFINE -e NOAN | cut -f3 | cut -d' ' -f1 | sed -e 's/diac://g' > tmp.txt
# grep pos:abbrev almor-msa-r13.db | grep -v -e DEFAULT -e DEFINE -e NOAN | cut -f1 >> tmp.txt
# camel_arclean tmp.txt | sort | uniq > abbrev.txt

ABBREV_SET = {'أ', 'إ', 'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي', 'آي', 'أر', 'أف', 'أو', 'أي', 'إس', 'إف', 'إل', 'إم', 'إن', 'إي', 'ار', 'اس', 'اف', 'ال', 'ام', 'ان', 'او', 'اي', 'بي', 'تغ', 'تي', 'جي', 'دي', 'سي', 'في', 'كم', 'مث', 'مم', 'يو', 'آلخ', 'ألخ', 'إلخ', 'إيه', 'اتش', 'الخ', 'ايه', 'كجم', 'كغم', 'كلج', 'كلغ', 'كلم', 'ملم', 'صلعم'}
# start with EOS or the space, followed by one of the abbreviations, followed by fullstop
_ABBREV_RE = u'((^| )((' + u'|'.join(ABBREV_SET) + u')(\.))+)'

# concatenated all the expressions using pipe
_ESCAPE_RE = re.compile(u'|'.join([_LINK_RE, _EMAIL_RE, _DECIMAL_RE, _ABBREV_RE]))


def escape_char_in_regex(s, char_to_escape='.', regex=''):
    '''Escape characters in the sequence that matches to a regular expression.
    Args:
        s (:obj:`str`):
            The string to be escaped.
        char_to_escape (:obj:`str`, defaults to "."):
            The character to escape.
        regex (:obj:`_sre.SRE_Pattern`):
            The regular expression pattern for the sequence to escape.
    Returns:
        s (:obj:`str`):
            The escaped string.
    '''

    escaped_text = ''
    current_index = 0

    for match in re.finditer(regex, s):
        # append the original text from the current index up to the begining of the matched sequence
        escaped_text += s[current_index:match.start()]
        matched = match.group(0)
        escaped = matched.replace(char_to_escape, '▁' + char_to_escape)
        # append the escaped sequence to the text
        escaped_text += escaped
        # update the current index
        current_index = match.end()
    # concatenate the sequence after the final match (or if it doesn't match anything)
    escaped_text += s[current_index:]
    return escaped_text


def _sent_tokenize_soft_delimiter(s, max_seq_len=100):
    """Split text into sentences.
    Args:
        s (:obj:`str`):
            The string to be segmented.
        max_seq_len (:obj:`int`, defaults to 100):
            The maximum sequence length of text before the soft delimiter. If a soft delimiter
            appears after this value, it will split on the first soft delimiter in the entire text.  
    Returns:
        :obj:`list` of :obj:`str`:
            The list of segmented string.
    """

    words = s.split(' ')

    if len(words) > max_seq_len:
        text_before_max = ' '.join(words[:max_seq_len])

        # commas before max sequence length -> split on the last comma
        if re.match(_SOFT_DELIMITER_RE, text_before_max):
            last_index = re.match(_SOFT_DELIMITER_RE, text_before_max).end()
            text_before_delimiter = s[:last_index]
            text_after_delimiter = s[last_index:].strip()
            return [text_before_delimiter, text_after_delimiter]

        # no comma in a sequence before max_seq_len -> do nothing
        else:
            return [s]

    # sequence is less than max_seq_len -> do nothing
    else:
        return [s]


def sent_tokenize(s, delimiter=_HARD_DELIMITER_RE, escape_regex=_ESCAPE_RE,
                  split_soft_delimiter=True, max_seq_len=100):
    """Split text into sentences.
    Args:
        s (:obj:`str`):
            The string to be segmented.
        delimiter (:obj:`_sre.SRE_Pattern`):
            The regular expression pattern for delimiters.
        escape_regex (:obj:`_sre.SRE_Pattern`):
            The regular expression pattern for the sequence to escape.
        split_soft_delimiter (obj: `bool`, defaults to True):
            Whether to split on soft delimiter.
        max_seq_len (:obj:`int`, defaults to 100):
            The maximum sequence length of text before the soft delimiter. If a soft delimiter
            appears after this value, it will split on the first soft delimiter in the entire text.
    Returns:
        :obj:`list` of :obj:`str`:
            The list of segmented string.
    """

    # escape with "▁"(U+2581)
    s = escape_char_in_regex(s, regex=escape_regex)

    sents = []
    start = 0
    for match in re.finditer(delimiter, s):
        end = match.end()
        sent = s[start:end].strip()
        sents.append(sent)
        start = end

    # if the end of matched sequence is not the end of the original sequence
    if start != len(s):
        sent = s[start:len(s)].strip()
        sents.append(sent)

    # remove escape character "▁"(U+2581)
    sents = [sent.replace('▁', '') for sent in sents]

    # remove empty sentences
    sents = [sent for sent in sents if sent]

    # if split on soft delimiter
    if split_soft_delimiter:
        soft_sents = []
        for sent in sents:
            soft_sent = _sent_tokenize_soft_delimiter(sent, max_seq_len)
            soft_sents.extend(soft_sent)
        return soft_sents

    # if split only on hard delimier
    else:
        return sents


def main():
    try:
        with open(sys.argv[1], mode='r', encoding='utf-8') as f:
            for line in f.readlines():
                if line != '\n':
                    for sent in sent_tokenize(line):
                        sys.stdout.write(sent + '\n')
                else:
                    sys.stdout.write('\n')

    except Exception:
        sys.stderr.write('Error: An unknown error occurred.\n')
        sys.exit(1)


if __name__ == '__main__':
    main()
