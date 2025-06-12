def determine_content_language(text):
    language = 'en'

    if ('ă' in text or 'â' in text or 'î' in text or 'ș' in text or 'ț' in text):
        language = 'ro'
    else:
        language = 'en'

    if language != 'en':
        if (' and ' in text or
            ' its ' in text or
            ' of ' in text or
            ' the ' in text or
            ' was ' in text):
            language = 'en'

    if language != 'ro':
        if (' de la ' in text or
            ' miliarde ' in text):
            language = 'ro'

    if (' al patrulea ' in text or
        'mbasadorul' in text or
        'interzis' in text):
        language = 'ro'

    return language