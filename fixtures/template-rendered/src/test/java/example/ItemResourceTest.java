package example;

import io.quarkus.test.junit.QuarkusTest;
import io.restassured.response.Response;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.validation.Validator;
import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static io.restassured.RestAssured.given;
import static org.junit.jupiter.api.Assertions.*;
import static org.hamcrest.Matchers.*;

@QuarkusTest
class ItemResourceTest {
    @Inject ItemRepository repository;
    @Inject SetterItemRepository setterRepository;
    @Inject ItemMapper mapper;
    @Inject FixtureSeeder seeder;
    @Inject Validator validator;

    @BeforeEach @Transactional void clear() {
        repository.deleteAll();
        setterRepository.deleteAll();
        Item.validationSequence.clear(); Item.validationStates.clear();
        ItemDto.validationSequence.clear(); ItemDto.validationStates.clear();
        SetterItem.validationSequence.clear(); SetterItem.validationStates.clear();
    }

    private long createItem(String name, String note, boolean required) {
        Number id = given().contentType("application/json")
            .body("{\"name\":\""+name+"\",\"note\":\""+note+"\",\"count\":3,\"noteRequired\":"+required+"}")
            .post("/items").then().statusCode(200).extract().path("id");
        return id.longValue();
    }

    private long createDto(String name, String note) {
        Number id = given().contentType("application/json")
            .body("{\"id\":999,\"name\":\""+name+"\",\"note\":\""+note+"\",\"count\":2,\"active\":true,\"longValue\":17,\"ratio\":1.25,\"amount\":\"12.50\",\"token\":\"123e4567-e89b-12d3-a456-426614174000\",\"state\":\"READY\",\"serverValue\":\"attacker\",\"version\":99,\"noteRequired\":true}")
            .post("/dto-items").then().statusCode(200).body("id", not(999)).body("serverValue", is("server-owned")).body("version", is(0)).body("noteRequired", is(false)).extract().path("id");
        return id.longValue();
    }

    @Test void publicEntitySortedPaginationAndBounds() {
        createItem("zulu", "old", false); createItem("alpha", "old", false);
        given().queryParam("page",0).queryParam("size",1).get("/items").then().statusCode(200).body("size()", is(1)).body("[0].name", is("alpha"));
        given().queryParam("size",101).get("/items").then().statusCode(400);
        given().queryParam("page",-1).get("/items").then().statusCode(400);
    }

    @Test void publicPatchConversionsAndRejectsUntrustedPayloads() {
        long id=createItem("before", "keep", false);
        given().contentType("application/json").body("{}").patch("/items/"+id).then().statusCode(200).body("name", is("before"));
        given().contentType("application/json").body("{\"name\":\"good\",\"note\":null,\"count\":5,\"active\":true,\"longValue\":42,\"ratio\":1.5,\"amount\":\"12.50\",\"token\":\"123e4567-e89b-12d3-a456-426614174000\",\"state\":\"READY\"}")
            .patch("/items/"+id).then().statusCode(200).body("name",is("good")).body("note",nullValue()).body("count",is(5)).body("active",is(true)).body("longValue",is(42)).body("ratio",is(1.5f)).body("amount",is(12.5f)).body("token",is("123e4567-e89b-12d3-a456-426614174000")).body("state",is("READY"));
        String secret="DO_NOT_ECHO_9ac81";
        String[] invalid={"null","[]","\"text\"","{\"unknown\":1}","{\"id\":999}","{\"version\":99}","{\"serverValue\":\""+secret+"\"}","{\"noteRequired\":true}","{\"name\":{}}","{\"name\":[]}","{\"name\":12}","{\"count\":\"12\"}","{\"active\":\"true\"}","{\"count\":2147483648}","{\"longValue\":9223372036854775808}","{\"ratio\":1e309}","{\"count\":null}","{\"amount\":12.5}","{\"amount\":\"not-decimal-"+secret+"\"}","{\"token\":\"bad-"+secret+"\"}","{\"state\":\"MISSING\"}"};
        for (String body : invalid) {
            Response response=given().contentType("application/json").body(body).patch("/items/"+id).then().statusCode(400).extract().response();
            assertFalse(response.asString().contains(secret), "error echoed submitted secret");
        }
        given().get("/items/"+id).then().statusCode(200).body("name",is("good")).body("note",nullValue()).body("count",is(5)).body("serverValue",is("server-owned")).body("version",is(0)).body("noteRequired",is(false));
        given().contentType("application/json").body("{\"count\":1}").patch("/items?ids=9223372036854770000").then().statusCode(200).body("size()",is(0));
    }

    @Test void publicEntityValidationRejectsMutationWithoutPersisting() {
        long id=createItem("valid", "old", false);
        given().contentType("application/json").body("{\"name\":\"\"}").patch("/items/"+id).then().statusCode(400);
        given().get("/items/"+id).then().statusCode(200).body("name",is("valid"));
    }

    @Test void publicPatchManyValidFirstThenInvalidRollsBackBothRows() {
        long first=createItem("first", "old", false), second=createItem("second", "old", true);
        assertTrue(first < second);
        Item.validationSequence.clear(); Item.validationStates.clear();
        given().contentType("application/json").body("{\"note\":null}").patch("/items?ids="+first+"&ids="+second).then().statusCode(400);
        assertTrue(Item.validationSequence.indexOf(first) >= 0 && Item.validationSequence.indexOf(second) > Item.validationSequence.indexOf(first), "fixture repository must validate the lower id before the failing later row: " + Item.validationSequence);
        assertTrue(Item.validationStates.indexOf(first + ":null") >= 0 && Item.validationStates.indexOf(second + ":null") > Item.validationStates.indexOf(first + ":null"), "validator observed the first actual mutation before the later invalid item: " + Item.validationStates);
        given().get("/items/"+first).then().statusCode(200).body("note",is("old"));
        given().get("/items/"+second).then().statusCode(200).body("note",is("old"));
    }

    @Test void mapperIsCdiAndRenderedSafeUpdatePreservesProtectedFields() {
        assertNotNull(mapper);
        Item entity=new Item(); entity.id=81L; entity.name="old"; entity.serverValue="server-owned"; entity.version=7;
        mapper.partialUpdate(new ItemDto(null,"new",null,4,true,5,1.5,null,null,Item.State.READY,"attacker",99,true),entity);
        assertEquals("new",entity.name); assertEquals(81L,entity.id); assertEquals("server-owned",entity.serverValue);
        assertEquals(7L,entity.version); assertFalse(entity.noteRequired);
    }

    @Test void dtoCreatePatchConversionsAndProtectedProperties() {
        long id=createDto("dto-before", "old");
        given().contentType("application/json").body("{}").patch("/dto-items/"+id).then().statusCode(200).body("name",is("dto-before")).body("count",is(2));
        given().get("/dto-items/"+id).then().statusCode(200).body("id",is((int)id)).body("serverValue",is("server-owned"));
        given().contentType("application/json").body("{\"name\":\"dto-after\",\"note\":null,\"count\":8,\"active\":false,\"longValue\":43,\"ratio\":2.5,\"amount\":\"0.125\",\"token\":\"123e4567-e89b-12d3-a456-426614174001\",\"state\":\"NEW\"}")
            .patch("/dto-items/"+id).then().statusCode(200).body("name",is("dto-after")).body("note",nullValue()).body("count",is(8)).body("active",is(false)).body("longValue",is(43)).body("ratio",is(2.5f)).body("amount",is(0.125f)).body("token",is("123e4567-e89b-12d3-a456-426614174001")).body("state",is("NEW")).body("serverValue",is("server-owned"));
        for (String body : new String[]{"null","[]","\"text\"","{\"unknown\":1}","{\"id\":1}","{\"version\":5}","{\"serverValue\":\"attacker\"}","{\"noteRequired\":true}","{\"name\":{}}","{\"name\":[]}","{\"count\":\"12\"}","{\"active\":\"yes\"}","{\"name\":42}","{\"count\":null}","{\"active\":null}","{\"longValue\":null}","{\"longValue\":9223372036854775808}","{\"ratio\":1e309}","{\"amount\":12.5}","{\"amount\":\"bad\"}","{\"token\":\"bad\"}","{\"state\":\"NOPE\"}"})
            given().contentType("application/json").body(body).patch("/dto-items/"+id).then().statusCode(400);
        String sentinel="DO_NOT_ECHO_DTO_741";
        Response response=given().contentType("application/json").body("{\"token\":\""+sentinel+"\"}").patch("/dto-items/"+id).then().statusCode(400).extract().response();
        assertFalse(response.asString().contains(sentinel));
        given().get("/dto-items/"+id).then().statusCode(200).body("id",is((int)id)).body("name",is("dto-after")).body("note",nullValue()).body("count",is(8)).body("serverValue",is("server-owned")).body("version",is(0)).body("noteRequired",is(false));
        given().contentType("application/json").body("{\"count\":1}").patch("/dto-items?ids=9223372036854770000").then().statusCode(200).body("size()",is(0));
    }

    @Test void dtoOnlyConstraintRejectsAndEntityConstraintRunsAfterMerge() {
        long ordinary=createDto("valid", "old");
        assertTrue(validator.validate(repository.findById(ordinary)).isEmpty(), "entity constraints permit the value rejected only by the DTO");
        given().contentType("application/json").body("{\"note\":\"123456789012345678901\"}").patch("/dto-items/"+ordinary).then().statusCode(400);
        given().get("/dto-items/"+ordinary).then().statusCode(200).body("note",is("old"));
        long required;
        required=seeder.item("required", "old", true);
        given().contentType("application/json").body("{\"note\":null}").patch("/dto-items/"+required).then().statusCode(400);
        given().get("/dto-items/"+required).then().statusCode(200).body("note",is("old"));
    }

    @Test void dtoPatchManyProvesEarlierSuccessfulMutationThenFullRollback() {
        long first=seeder.item("first", "old", false);
        long second=seeder.item("second", "old", true); assertTrue(first < second);
        Item.validationSequence.clear(); Item.validationStates.clear(); ItemDto.validationSequence.clear(); ItemDto.validationStates.clear();
        given().contentType("application/json").body("{\"note\":null}").patch("/dto-items?ids="+first+"&ids="+second).then().statusCode(400);
        assertTrue(ItemDto.validationSequence.indexOf(first) >= 0 && ItemDto.validationSequence.indexOf(second) > ItemDto.validationSequence.indexOf(first), "DTO validation order: " + ItemDto.validationSequence);
        assertTrue(ItemDto.validationStates.indexOf(first + ":null") >= 0 && ItemDto.validationStates.indexOf(second + ":null") > ItemDto.validationStates.indexOf(first + ":null"), "DTO observed the first null merge before later failure: " + ItemDto.validationStates);
        assertTrue(Item.validationSequence.indexOf(first) >= 0 && Item.validationSequence.indexOf(second) > Item.validationSequence.indexOf(first), "entity validation order: " + Item.validationSequence);
        assertTrue(Item.validationStates.indexOf(first + ":null") >= 0 && Item.validationStates.indexOf(second + ":null") > Item.validationStates.indexOf(first + ":null"), "entity validated the first actual null mutation before the failing later item: " + Item.validationStates);
        given().get("/dto-items/"+first).then().statusCode(200).body("note",is("old"));
        given().get("/dto-items/"+second).then().statusCode(200).body("note",is("old"));
    }

    @Test void privateSetterResourceSupportsPatchAndBatchRollback() {
        Number id=given().contentType("application/json").body("{\"name\":\"setter\",\"count\":2}").post("/setter-items").then().statusCode(200).extract().path("id");
        long row=id.longValue();
        given().contentType("application/json").body("{\"name\":null,\"count\":4}").patch("/setter-items/"+row).then().statusCode(200).body("name",nullValue()).body("count",is(4));
        given().contentType("application/json").body("{\"count\":-1}").patch("/setter-items/"+row).then().statusCode(400);
        given().get("/setter-items/"+row).then().statusCode(200).body("count",is(4)).body("serverValue",is("server-owned"));
        given().contentType("application/json").body("{\"serverValue\":\"secret\"}").patch("/setter-items/"+row).then().statusCode(400);
        given().contentType("application/json").body("{\"countMustStayPositive\":true}").patch("/setter-items/"+row).then().statusCode(400);
    }

    @Test void privateSetterPatchManySuccessUpdatesEverySelectedRow() {
        Number first=given().contentType("application/json").body("{\"name\":\"first\",\"count\":1}").post("/setter-items").then().statusCode(200).extract().path("id");
        Number second=given().contentType("application/json").body("{\"name\":\"second\",\"count\":2}").post("/setter-items").then().statusCode(200).extract().path("id");
        given().contentType("application/json").body("{\"count\":8}").patch("/setter-items?ids="+first+"&ids="+second).then().statusCode(200).body("size()",is(2));
        given().get("/setter-items/"+first).then().statusCode(200).body("count",is(8));
        given().get("/setter-items/"+second).then().statusCode(200).body("count",is(8));
    }

    @Test void privateSetterBatchValidFirstThenInvalidRollsBackAllRows() {
        long first=seeder.setterItem("first", 2, false);
        long second=seeder.setterItem("second", 3, true); assertTrue(first < second); SetterItem.validationSequence.clear(); SetterItem.validationStates.clear();
        given().contentType("application/json").body("{\"count\":0}").patch("/setter-items?ids="+first+"&ids="+second).then().statusCode(400);
        assertTrue(SetterItem.validationSequence.indexOf(first) >= 0 && SetterItem.validationSequence.indexOf(second) > SetterItem.validationSequence.indexOf(first), "setter entity validation order: " + SetterItem.validationSequence);
        assertTrue(SetterItem.validationStates.indexOf(first + ":0") >= 0 && SetterItem.validationStates.indexOf(second + ":0") > SetterItem.validationStates.indexOf(first + ":0"), "setter observed first actual count mutation before later failure: " + SetterItem.validationStates);
        given().get("/setter-items/"+first).then().statusCode(200).body("count",is(2));
        given().get("/setter-items/"+second).then().statusCode(200).body("count",is(3));
    }
}
