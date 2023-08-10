using UnityEngine;
using UnityEditor;

public class SaveRenderTextureToFile : EditorWindow
{
	private RenderTexture rt;
	private bool autoRenderFrames;
	private bool isRenderingPaused;
	private int framesPerSecond = 24; // Set to 24 FPS
	private int frameNumber;
	private float frameInterval;

	[MenuItem("BENCGN/Save RenderTexture to file &q")]
	public static void ShowWindow()
	{
		EditorWindow.GetWindow<SaveRenderTextureToFile>("Save RT to File");
	}

	private void OnGUI()
	{
		GUILayout.Label("Save RenderTexture to file", EditorStyles.boldLabel);

		rt = EditorGUILayout.ObjectField("RenderTexture", rt, typeof(RenderTexture), true) as RenderTexture;

		if (GUILayout.Button("Save Current Frame"))
		{
			SaveRTToFile();
		}

		GUILayout.Space(10);
		GUILayout.Label("Auto Render Frames", EditorStyles.boldLabel);
		autoRenderFrames = EditorGUILayout.Toggle("Enable Auto Render", autoRenderFrames);

		EditorGUI.BeginDisabledGroup(!autoRenderFrames); // Disable other controls while auto-rendering is enabled
		{
			framesPerSecond = EditorGUILayout.IntField("Frames Per Second", framesPerSecond);

			// Increase the size of the buttons for better visibility
			if (GUILayout.Button("Start Auto Render", GUILayout.Height(30)))
			{
				frameNumber = 0; // Reset frame number before starting auto-rendering
				frameInterval = 1f / framesPerSecond; // Calculate the frame interval based on FPS
				EditorApplication.update += AutoRenderFrames;
				isRenderingPaused = false;
			}

			if (GUILayout.Button("Pause Auto Render", GUILayout.Height(30)))
			{
				isRenderingPaused = !isRenderingPaused;
			}

			if (GUILayout.Button("Stop Auto Render", GUILayout.Height(30)))
			{
				EditorApplication.update -= AutoRenderFrames;
			}
		}
		EditorGUI.EndDisabledGroup();
	}

	private void SaveRTToFile()
	{
		if (rt == null)
		{
			Debug.LogError("No RenderTexture selected!");
			return;
		}

		RenderTexture.active = rt;
		Texture2D tex = new Texture2D(rt.width, rt.height, TextureFormat.RGBA32, false);
		tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
		RenderTexture.active = null;

		byte[] bytes;
		bytes = tex.EncodeToPNG();

		string folderPath = "D:/renderunity/";
		string fileName = rt.name + "_Frame_" + frameNumber + ".png";
		string fullPath = folderPath + fileName;

		System.IO.Directory.CreateDirectory(folderPath);
		System.IO.File.WriteAllBytes(fullPath, bytes);

		AssetDatabase.Refresh();

		Debug.Log("Saved frame " + frameNumber + " to " + fullPath);

		frameNumber++; // Increment frame number after saving
	}

	private void AutoRenderFrames()
	{
		if (autoRenderFrames && rt != null && !isRenderingPaused)
		{
			SaveRTToFile();

			// Wait for the specified frame interval before rendering the next frame
			if (frameInterval > 0f)
			{
				System.Threading.Thread.Sleep((int)(frameInterval * 1000f));
			}
		}
	}
}
