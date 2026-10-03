package example;

import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.AssertTrue;
import jakarta.validation.constraints.Min;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

@jakarta.persistence.Entity
@Table(name = "setter_items")
public class SetterItem {
    public static final List<Long> validationSequence = new CopyOnWriteArrayList<>();
    public static final List<String> validationStates = new CopyOnWriteArrayList<>();
    @Id @GeneratedValue public Long id;
    private String name;
    @Min(0) private int count;
    private String serverValue = "server-owned";
    private boolean countMustStayPositive;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getCount() { return count; }
    public void setCount(int count) { this.count = count; }
    public String getServerValue() { return serverValue; }
    public void setServerValue(String serverValue) { this.serverValue = serverValue; }
    public boolean isCountMustStayPositive() { return countMustStayPositive; }
    public void setCountMustStayPositive(boolean value) { this.countMustStayPositive = value; }
    @AssertTrue public boolean isCountInvariant() { validationSequence.add(id); validationStates.add(id + ":" + count); return !countMustStayPositive || count > 0; }
}
