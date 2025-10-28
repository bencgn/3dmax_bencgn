"""
Meshcapade T-Pose Inserter for Maya
Version: 3.0.0
Author: Technical Artist Pipeline Tools

Description:
    Inserts a T-pose at the current frame by setting all joint rotations to 0,0,0.
    Uses wherever the timeline cursor is positioned.
    Perfect for Meshcapade rigs.

Usage:
    1. Move timeline to desired frame (usually frame 0)
    2. Select the root of your Meshcapade rig (usually 'pelvis' or 'root')
    3. Run: insert_tpose_frame()
"""

import maya.cmds as cmds


class MeshcapadeTPoseInserter:
    """Inserts T-pose at current frame for Meshcapade SMPL rigs in Maya"""
    
    # Standard SMPL bone names used by Meshcapade
    SMPL_BONE_NAMES = [
        'pelvis', 'root',
        'left_hip', 'right_hip',
        'spine1', 'spine2', 'spine3', 'spine',
        'left_knee', 'right_knee',
        'left_ankle', 'right_ankle',
        'left_foot', 'right_foot',
        'neck', 'head',
        'left_collar', 'right_collar',
        'left_shoulder', 'right_shoulder',
        'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist',
        'left_hand', 'right_hand',
        # SMPL-X hand joints
        'left_index1', 'left_index2', 'left_index3',
        'left_middle1', 'left_middle2', 'left_middle3',
        'left_pinky1', 'left_pinky2', 'left_pinky3',
        'left_ring1', 'left_ring2', 'left_ring3',
        'left_thumb1', 'left_thumb2', 'left_thumb3',
        'right_index1', 'right_index2', 'right_index3',
        'right_middle1', 'right_middle2', 'right_middle3',
        'right_pinky1', 'right_pinky2', 'right_pinky3',
        'right_ring1', 'right_ring2', 'right_ring3',
        'right_thumb1', 'right_thumb2', 'right_thumb3',
        'left_eye', 'right_eye', 'jaw'
    ]
    
    def __init__(self):
        self.rig_root = None
        self.all_joints = []
        self.target_frame = None
        
    def validate_selection(self):
        """Validates that a proper rig is selected"""
        selection = cmds.ls(selection=True, long=True)
        
        if not selection:
            cmds.warning("Please select the root of your Meshcapade rig")
            return False
            
        self.rig_root = selection[0]
        
        # Get current frame
        self.target_frame = cmds.currentTime(query=True)
        
        # Get all descendants (joints and transforms)
        descendants = cmds.listRelatives(self.rig_root, allDescendents=True, 
                                        fullPath=True) or []
        
        # Filter to only joints
        joints = [j for j in descendants if cmds.nodeType(j) == 'joint']
        
        if not joints:
            # Try checking if selected object itself is a joint
            if cmds.nodeType(self.rig_root) == 'joint':
                joints = cmds.listRelatives(self.rig_root, allDescendents=True, 
                                           type='joint', fullPath=True) or []
                joints.append(self.rig_root)
            else:
                cmds.warning(f"No joints found under {self.rig_root}")
                return False
        
        self.all_joints = joints
        print(f"Found {len(self.all_joints)} joints in rig hierarchy")
        print(f"Target frame: {int(self.target_frame)}")
        
        # Verify this looks like a Meshcapade rig
        joint_names = [cmds.ls(j, shortNames=True)[0].lower() for j in self.all_joints]
        meshcapade_matches = sum(1 for name in joint_names 
                                if any(smpl_name in name for smpl_name in self.SMPL_BONE_NAMES))
        
        if meshcapade_matches < 5:
            result = cmds.confirmDialog(
                title='Rig Verification',
                message=f'Only found {meshcapade_matches} Meshcapade-style bone names.\n'
                       f'This might not be a Meshcapade rig.\n\n'
                       f'Continue anyway?',
                button=['Yes', 'No'],
                defaultButton='No',
                cancelButton='No',
                dismissString='No'
            )
            if result != 'Yes':
                return False
        
        return True
    
    def apply_tpose_at_current_frame(self):
        """Sets all joint rotations to 0,0,0 at current frame (creates T-pose)"""
        print(f"\n--- Applying T-Pose at Frame {int(self.target_frame)} ---")
        
        # Make sure we're at the target frame
        cmds.currentTime(self.target_frame)
        
        joints_keyed = 0
        joints_skipped = 0
        
        # Zero out all joint rotations at current frame
        for joint in self.all_joints:
            try:
                # Check if rotation channels are unlocked and keyable
                rotate_attrs = ['rotateX', 'rotateY', 'rotateZ']
                channels_set = 0
                
                for attr in rotate_attrs:
                    attr_full = f"{joint}.{attr}"
                    
                    # Check if attribute exists and is not locked
                    if cmds.objExists(attr_full):
                        is_locked = cmds.getAttr(attr_full, lock=True)
                        
                        if not is_locked:
                            # Set to zero
                            cmds.setAttr(attr_full, 0)
                            channels_set += 1
                
                # Only keyframe if we successfully set at least one channel
                if channels_set > 0:
                    cmds.setKeyframe(joint, attribute='rotate', time=self.target_frame)
                    joints_keyed += 1
                else:
                    joints_skipped += 1
                
            except Exception as e:
                print(f"Warning: Could not process joint {joint}: {e}")
                joints_skipped += 1
        
        print(f"✓ Set T-pose for {joints_keyed} joints")
        if joints_skipped > 0:
            print(f"  Skipped {joints_skipped} locked/unavailable joints")
        
        return True
    
    def execute(self):
        """Main execution function"""
        print("\n" + "="*70)
        print("MESHCAPADE T-POSE INSERTER - Current Frame")
        print("="*70)
        
        # Validation
        if not self.validate_selection():
            return False
        
        # Confirm with user
        result = cmds.confirmDialog(
            title='Insert T-Pose at Current Frame',
            message=f'This will:\n'
                   f'1. Set all joint rotations to 0,0,0 at current frame\n'
                   f'2. Create keyframes at current frame for T-pose\n'
                   f'3. Leave all other frames unchanged\n\n'
                   f'Selected rig: {self.rig_root.split("|")[-1]}\n'
                   f'Joints found: {len(self.all_joints)}\n'
                   f'Target frame: {int(self.target_frame)}\n\n'
                   f'Continue?',
            button=['Yes', 'No'],
            defaultButton='Yes',
            cancelButton='No',
            dismissString='No'
        )
        
        if result != 'Yes':
            print("Operation cancelled by user")
            return False
        
        # Execute
        try:
            if not self.apply_tpose_at_current_frame():
                cmds.warning("Failed to apply T-pose")
                return False
            
            # Success message
            cmds.confirmDialog(
                title='Success',
                message=f'T-pose inserted at frame {int(self.target_frame)}!\n\n'
                       f'Frame {int(self.target_frame)}: T-pose (all rotations = 0)\n'
                       f'Other frames: Unchanged\n\n'
                       f'Joints processed: {len(self.all_joints)}',
                button=['OK']
            )
            
            print("\n" + "="*70)
            print(f"SUCCESS: T-pose created at frame {int(self.target_frame)}")
            print(f"All {len(self.all_joints)} joints set to zero rotation")
            print("Other frames preserved")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            cmds.error(f"Error during execution: {e}")
            import traceback
            traceback.print_exc()
            return False


def insert_tpose_frame():
    """
    Main function to insert T-pose at current frame.
    
    Usage:
        1. Move timeline to desired frame (usually frame 0)
        2. Select the root of your Meshcapade rig (pelvis or root joint)
        3. Run this function
        4. Current frame will be set to T-pose
    """
    inserter = MeshcapadeTPoseInserter()
    return inserter.execute()


# Convenience function for shelf button
def run():
    """Quick run function for shelf buttons"""
    insert_tpose_frame()


if __name__ == "__main__":
    insert_tpose_frame()
