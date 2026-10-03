package example;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;

@Mapper(componentModel = "cdi")
public interface ItemMapper {
    ItemDto toItemDto(Item entity);

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "serverValue", ignore = true)
    @Mapping(target = "version", ignore = true)
    @Mapping(target = "noteRequired", ignore = true)
    Item toEntity(ItemDto dto);

    // SAFE_PATCH_METHOD
}
