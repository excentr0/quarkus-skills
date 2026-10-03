package example;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;

@ApplicationScoped
public class FixtureSeeder {
    @Inject ItemRepository items;
    @Inject SetterItemRepository setterItems;

    @Transactional public long item(String name, String note, boolean noteRequired) {
        Item row = new Item(); row.name = name; row.note = note; row.noteRequired = noteRequired;
        items.persistAndFlush(row); return row.id;
    }

    @Transactional public long setterItem(String name, int count, boolean countMustStayPositive) {
        SetterItem row = new SetterItem(); row.setName(name); row.setCount(count);
        row.setCountMustStayPositive(countMustStayPositive); setterItems.persistAndFlush(row); return row.id;
    }
}
