using UMA.PoseTools;
using UnityEngine;

public class OverrideMechanim : MonoBehaviour
{
    [SerializeField] ExpressionPlayer expressionPlayer;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        expressionPlayer.overrideMecanimEyes = true;
        expressionPlayer.overrideMecanimHead = true;
        expressionPlayer.overrideMecanimJaw = true;
    }
}
