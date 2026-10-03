package example;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;

public record ItemDto(Long id, @NotBlank String name, @Size(max = 20) String note,
        @Min(0) int count, boolean active, long longValue, double ratio,
        BigDecimal amount, UUID token, Item.State state,
        String serverValue, long version, boolean noteRequired) {
    public static final List<Long> validationSequence = new CopyOnWriteArrayList<>();
    public static final List<String> validationStates = new CopyOnWriteArrayList<>();
    @jakarta.validation.constraints.AssertTrue public boolean isValidationWitness() {
        validationSequence.add(id);
        validationStates.add(id + ":" + note);
        return true;
    }
}
