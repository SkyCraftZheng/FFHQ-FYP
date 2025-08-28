using UnityEngine;
using UMA;
using UMA.CharacterSystem;

public class Buttons : MonoBehaviour
{
    [SerializeField] DynamicCharacterAvatar dca;
    [SerializeField] UMATextRecipe original_dna;
    [SerializeField] UMATextRecipe new_dna;
    [SerializeField] RaceData race;
    public void originalB()
    {
        race.baseRaceRecipe = original_dna;
        dca.ClearSlot("Face");
        dca.ClearSlot("AlternateHead");
        dca.ClearSlot("Eyes");
        dca.ClearSlot("Complexion");
        dca.BuildCharacter();
    }

    public void processed()
    {
        race.baseRaceRecipe = original_dna;
        dca.ClearSlot("Face");
        dca.ClearSlot("AlternateHead");
        dca.ClearSlot("Eyes");
        dca.ClearSlot("Complexion");
        dca.SetSlot("stage3_mesh_id_Recipe");
        dca.SetSlot("eyes_Recipe");
        dca.SetSlot("inner_mouth_Recipe");
        dca.SetSlot("SkinToneRecipe");
        dca.BuildCharacter();
    }

    public void DNAconformed()
    {
        race.baseRaceRecipe = new_dna;
        dca.ClearSlot("Face");
        dca.ClearSlot("AlternateHead");
        dca.ClearSlot("Eyes");
        dca.ClearSlot("Complexion");
        dca.SetSlot("TestOverlayRecipe");
        dca.BuildCharacter();
    }

    public void Hair1()
    {
        dca.ClearSlot("Hair");
        dca.SetSlot("FemaleHair1");
        dca.BuildCharacter();
    }

    public void Hair2()
    {
        dca.ClearSlot("Hair");
        dca.SetSlot("FemaleHair2");
        dca.BuildCharacter();
    }

    public void Hair3()
    {
        dca.ClearSlot("Hair");
        dca.SetSlot("FemaleHair3");
        dca.BuildCharacter();
    }

    public void NoHair()
    {
        dca.ClearSlot("Hair");
        dca.BuildCharacter();
    }
}
