package example;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.Comparator;
import java.util.List;

/** Test fixture ordering for the template's id-IN batch query; not production repository guidance. */
@ApplicationScoped
public class ItemRepository implements PanacheRepository<Item> {
    @Override public List<Item> list(String query, Object... params) {
        List<Item> rows = find(query, params).list();
        rows.sort(Comparator.comparing(item -> item.id));
        return rows;
    }
}
