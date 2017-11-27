# DMItem["API field"] = "DB column"
DMItem = {}
DMItem["accountBound"] = "accountBound"
DMItem["Ancient_Rank"] = "ancientRank"
DMItem["Armor_Item"] = "armorItem"
# DMItem["armor"] = "armor"
DMItem["attacksPerSecond"] = "attacksPerSecond"
# DMItem["attacksPerSecondText"] = "attacksPerSecondText"
# DMItem["attributes"] = ""
# DMItem["attributesRaw"] = ""
DMItem["augmentation"] = "augmentation"
DMItem["blockChance"] = "blockChance"
# DMItem["bonusAffixes"] = ""
# DMItem["bonusAffixesMax"] = ""
# DMItem["craftedBy"] = "craftedBy"
DMItem["Crit_Damage_Percent"] = "critDamage"
DMItem["CubeEnchantedGemRank"] = "cubeEnchantedGemRank"
DMItem["CubeEnchantedGemType"] = "cubeEnchantedGemType"
# DMItem["damageRange"] = "damageRange"
# DMItem["description"] = ""
DMItem["Dexterity_Item"] = "dexterity"
DMItem["displayColor"] = "displayColor"
DMItem["dps"] = "dps"
DMItem["Durability_Cur"] = "durabilityCurrent"
DMItem["Durability_Max"] = "durabilityMax"
# DMItem["dyeColor"] = ""
DMItem["elementalType"] = "elementalType"
# DMItem["flavorText"] = ""
DMItem["gems"] = "gems"
DMItem["Gold_Find"] = "goldFind"
DMItem["icon"] = "icon"
DMItem["id"] = "itemId"
# DMItem["isSeasonRequiredToDrop"] = ""
DMItem["itemLevel"] = "itemLevel"
DMItem["maxDamage"] = "maxDamage"
DMItem["minDamage"] = "minDamage"
DMItem["name"] = "name"
# DMItem["randomAffixes"] = ""
# DMItem["recipe"] = ""
DMItem["requiredLevel"] = "requiredLevel"
DMItem["Resistance#Cold"] = "resistanceCold"
# DMItem["seasonRequiredToDrop"] = ""
# DMItem["set"] = ""
# DMItem["setItemsEquipped"] = ""
# DMItem["slots"] = ""
# DMItem["socketEffects"] = ""
# DMItem["stackSizeMax"] = ""
DMItem["tooltipParams"] = "tooltipParams"
# DMItem["transmogItem"] = ""
# DMItem["type"] = ""
DMItem["typeName"] = "typeName"
DMItem["Vitality_Item"] = "vitality"


# returns field only
def _db(apiField):
    if (apiField in DMItem):
        return DMItem[apiField]

    return None


# returns table and field
def dbMap(apiField):
    if (apiField in DMItem):
        return {'table': 'itemDetail', 'field': DMItem[apiField]}

    return None
