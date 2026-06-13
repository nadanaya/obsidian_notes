Safely Changing Patient Status in a Hospital System using Supabase RPC Functions

The goal is to safely change the status of waiting patients in a hospital system by creating a single DB transaction function that updates the patient's status, resets the waiting number, and moves on to the next patient.

To achieve this, two Supabase RPC functions are proposed: `start_treatment` and `complete_treatment`. The `start_treatment` function will update the patient's status to "진료", reset the waiting number, and move on to the next patient. The `complete_treatment` function will update the patient's status to "완료".

The implementation involves creating two Supabase RPC functions using SQL Editor: `start_treatment` and `complete_treatment`. These functions are executed using Supabase RPC calls from the front-end.

Benefits of this approach include:

* **Safety**: The DB transaction ensures that the status changes are atomic, and either all or none of the updates will be applied.
* **Consistency**: The front-end will not receive inconsistent data, as the status changes are executed in a single DB transaction.
* **Efficiency**: The DB transaction reduces the number of queries required to update the patient's status.