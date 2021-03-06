from django.core.paginator import (Paginator, Page, PageNotAnInteger,
                                   EmptyPage)
from django.db import connection


class InfinitePaginator(Paginator):
    """
    Paginator designed for cases when it's not important to know how many
    total pages.  This is useful for any object_list that has no count()
    method or can be used to improve performance for MySQL by removing counts.

    The orphans parameter has been removed for simplicity and there's a link
    template string for creating the links to the next and previous pages.
    """

    def __init__(self, object_list, per_page, allow_empty_first_page=True,
        link_template='/page/%d/', orphans=0):
        orphans = 0 # no orphans
        super(InfinitePaginator, self).__init__(object_list, per_page, orphans,
            allow_empty_first_page)
        # no count or num pages
        del self._num_pages, self._count
        # bonus links
        self.link_template = link_template

    def validate_number(self, number):
        """
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except ValueError:
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        return number

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        page_items = self.object_list[bottom:top]
        # check moved from validate_number
        if not page_items:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage('That page contains no results')
        return InfinitePage(page_items, number, self)

    def _get_count(self):
        """
        Returns the total number of objects, across all pages.
        """
        raise NotImplementedError
    count = property(_get_count)

    def _get_num_pages(self):
        """
        Returns the total number of pages.
        """
        raise NotImplementedError
    num_pages = property(_get_num_pages)

    def _get_page_range(self):
        """
        Returns a 1-based range of pages for iterating through within
        a template for loop.
        """
        raise NotImplementedError
    page_range = property(_get_page_range)


class InfinitePage(Page):

    def __repr__(self):
        return '<Page %s>' % self.number

    def has_next(self):
        """
        Checks for one more item than last on this page.
        """
        try:
            next_item = self.paginator.object_list[
                self.number * self.paginator.per_page]
        except IndexError:
            return False
        return True

    def end_index(self):
        """
        Returns the 1-based index of the last object on this page,
        relative to total objects found (hits).
        """
        return ((self.number - 1) * self.paginator.per_page +
            len(self.object_list))

    #Bonus methods for creating links

    def next_link(self):
        if self.has_next():
            return self.paginator.link_template % (self.number + 1)
        return None

    def previous_link(self):
        if self.has_previous():
            return self.paginator.link_template % (self.number - 1)
        return None


class PostgresLargeTablePaginator(Paginator):
    """
    Uses postgres pg_class to get a an estimated value, for the size of the
    table. If the value is below 10,000 it will do a COUNT(*) on the table.

    Also if there is a where filter on the query it will use count()
    """

    def _get_count(self):
        """
        Overwrite count to use custom logic of postgres.
        """
        if self._count is None:
            try:
                estimate = 0
                if not self.object_list.query.where:
                    try:
                        cursor = connection.cursor()
                        cursor.execute(
                            "SELECT reltuples FROM pg_class WHERE relname = %s",
                            [self.object_list.query.model._meta.db_table])
                        estimate = int(cursor.fetchone()[0])
                    except:
                        pass
                if estimate < 10000:
                    self._count = self.object_list.count()
                else:
                    self._count = estimate
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)