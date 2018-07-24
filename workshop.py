import logging
import xml.etree.ElementTree as Et


class WorkshopParser:
    NULL_SCORE_VALUE = '$@NULL@$'

    def __init__(self, workshop_file):
        self.xml = self._parse_xml(workshop_file)
        self.item_name = None
        self.cross_attempts = list()
        self._parse()
        self._item_name()

    @staticmethod
    def _parse_xml(file):
        return Et.parse(file)

    def _get_name(self):
        tags = self.xml.getiterator('name')
        if len(tags) == 0:
            logging.warning('Workshop.xml not contains <name>')
            return

        self.name = tags[0].text
        if len(tags) != 0:
            logging.warning('Workshop.xml contains many <name>. '
                            'Used first: {}'.format(self.name))

    @staticmethod
    def _check_found(**kwargs):
        for key, value in kwargs.items():
            if value is None:
                logging.warning('Not found "{}".'.format(key))
                return False
        return True

    @staticmethod
    def float_str_to_int(x):
        return int(float(x))

    def _parse(self):
        submissions = self.xml.getiterator('submission')
        for submission in submissions:
            author_id_tag = submission.find('authorid')
            if not self._check_found(authorid=author_id_tag):
                continue
            user_id = author_id_tag.text
            for assessment in submission.findall('.//assessment'):
                reviewerid_tag = assessment.find('reviewerid')
                grade_tag = assessment.find('grade')
                gradinggrade_tag = assessment.find('gradinggrade')

                if not self._check_found(reviewerid=reviewerid_tag,
                                         grade=grade_tag,
                                         gradinggrade=gradinggrade_tag):
                    continue

                reviewer_id = reviewerid_tag.text
                score = grade_tag.text
                max_score = gradinggrade_tag.text
                if score == self.NULL_SCORE_VALUE or \
                        max_score == self.NULL_SCORE_VALUE:
                    continue
                result = {'user_id': user_id, 'reviewer_id': reviewer_id,
                          'score': self.float_str_to_int(score), 'max_score': self.float_str_to_int(max_score)}
                self.cross_attempts.append(result)

    def _item_name(self):
        if self.item_name is None:
            name_tag = self.xml.getroot().find('./workshop/name')
            if not self._check_found(name=name_tag):
                raise Exception('Not found "name" tag')
            self.item_name = name_tag.text
        return self.item_name
