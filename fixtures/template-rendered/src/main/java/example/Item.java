package example;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.AssertTrue;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;

@Entity
@Table(name = "items")
public class Item {
    public static final List<Long> validationSequence = new CopyOnWriteArrayList<>();
    public static final List<String> validationStates = new CopyOnWriteArrayList<>();
    @Id @GeneratedValue public Long id;
    @NotBlank public String name;
    public String note;
    @Min(0) public int count;
    public boolean active;
    public long longValue;
    public double ratio;
    public BigDecimal amount;
    public UUID token;
    public State state = State.NEW;
    public String serverValue = "server-owned";
    public long version;
    public boolean noteRequired;

    public enum State { NEW, READY }
    @AssertTrue public boolean isNoteConsistent() { validationSequence.add(id); validationStates.add(id + ":" + note); return !noteRequired || note != null; }
}
