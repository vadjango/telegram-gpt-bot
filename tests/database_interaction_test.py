from unittest import TestCase, main
from db_interaction import add_user_to_database, delete_user_from_database
import psycopg2
from config import DB_CONFIG, TABLE_NAME


class Database(TestCase):

    def test_new_user_default_locale(self):
        add_user_to_database(988854)
        with psycopg2.connect(**DB_CONFIG) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT locale
                              FROM {TABLE_NAME}
                              WHERE user_id = 988854""")
            self.assertEqual(cursor.fetchall()[0][0], "en_US")
        delete_user_from_database(988854)


if __name__ == "__main__":
    main()
