import logging

import layout_scanner


def main():
    pdf_doc = '/home/stephane/Playground/PycharmProjects/TextMining/pdfs/2014/11/07/JT03365754.pdf'

    toc = layout_scanner.get_toc(pdf_doc)
    logger.debug('*'*40)
    logger.debug('Table Of Content:')
    logger.debug('*'*40)
    for elem in toc:
        logger.debug(elem[1].encode('utf-8'))

    pages = layout_scanner.get_pages(pdf_doc)

    logger.debug('*'*40)
    logger.debug('Text')
    logger.debug('*'*40)
    i = 0
    for elem in pages:
        logger.debug('-'*50)
        logger.debug('Page ' + str(i))
        logger.debug('-'*50)
        logger.debug(elem)
        i += 1


def logging_setup():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    _logger = logging.getLogger('pdf_layout')
    # create file handler which logs even debug messages
    fh = logging.FileHandler('summarizer.log', mode='w')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    _logger.addHandler(fh)
    _logger.addHandler(ch)

    return _logger

if __name__ == '__main__':
    logger = logging_setup()
    main()
