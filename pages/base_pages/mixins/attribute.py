import logging
from utils.exceptions import ValidationError

logger = logging.getLogger(__name__)

class AttributeMixin:
    """
    Mixin for manipulating HTML element attributes in Playwright tests.

    Provides async methods to remove or change attributes like 'required', 'maxlength', 'disabled', etc.,
    enabling advanced form and input testing.

    Requires: self.page (Playwright Page instance)
    """
    
    async def remove_required_attribute(self, selector: str) -> None:
        """
        Removes the 'required' attribute from the specified element.

        Args:
            selector (str): Selector for the element.

        Raises:
            ValidationError: If the attribute cannot be removed.

        Note:
            Useful for testing form validation by bypassing required field checks.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.removeAttribute('required')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to remove 'required' attribute: {str(e)}"
            ) from e

    async def remove_max_length_attribute(self, selector: str) -> None:
        """
        Removes the 'maxlength' attribute from the specified element.

        Args:
            selector (str): Selector for the element.

        Raises:
            ValidationError: If the attribute cannot be removed.

        Note:
            Useful for testing input validation beyond character limits.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.removeAttribute('maxlength')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to remove 'maxlength' attribute: {str(e)}"
            ) from e

    async def remove_min_length_attribute(self, selector: str) -> None:
        """
        Removes the 'minlength' attribute from the specified element.

        Args:
            selector (str): Selector for the element.

        Raises:
            ValidationError: If the attribute cannot be removed.

        Note:
            Useful for testing minimum length validation.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.removeAttribute('minlength')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to remove 'minlength' attribute: {str(e)}"
            ) from e

    async def remove_max_attribute(self, selector: str) -> None:
        """
        Removes the 'max' attribute from the specified element.

        Args:
            selector (str): Selector for the element.

        Raises:
            ValidationError: If the attribute cannot be removed.

        Note:
            Useful for testing maximum value validation on number/date inputs.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.removeAttribute('max')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to remove 'max' attribute: {str(e)}"
            ) from e

    async def remove_min_attribute(self, selector: str) -> None:
        """
        Removes the 'min' attribute from the specified element.

        Args:
            selector (str): Selector for the element.

        Raises:
            ValidationError: If the attribute cannot be removed.

        Note:
            Useful for testing minimum value validation on number/date inputs.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.removeAttribute('min')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to remove 'min' attribute: {str(e)}"
            ) from e

    async def remove_accept_attribute(self, selector: str) -> None:
        """
        Removes the 'accept' attribute from the specified element.

        Args:
            selector (str): Selector for the file input element.

        Raises:
            ValidationError: If the attribute cannot be removed.

        Note:
            Useful for testing file upload with different file types.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.removeAttribute('accept')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to remove 'accept' attribute: {str(e)}"
            ) from e

    async def remove_type_attribute(self, selector: str) -> None:
        """
        Removes the 'type' attribute from the specified element.

        Args:
            selector (str): Selector for the element.

        Raises:
            ValidationError: If the attribute cannot be removed.

        Note:
            Useful for testing input type validation.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.removeAttribute('type')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to remove 'type' attribute: {str(e)}"
            ) from e

    async def remove_pattern_attribute(self, selector: str) -> None:
        """
        Removes the 'pattern' attribute from the specified element.

        Args:
            selector (str): Selector for the element.

        Raises:
            ValidationError: If the attribute cannot be removed.

        Note:
            Useful for testing regex pattern validation.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.removeAttribute('pattern')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to remove 'pattern' attribute: {str(e)}"
            ) from e

    async def remove_disabled_attribute(self, selector: str) -> None:
        """
        Removes the 'disabled' attribute from the specified element.

        Args:
            selector (str): Selector for the element.

        Raises:
            ValidationError: If the attribute cannot be removed.

        Note:
            Useful for testing interactions with disabled elements.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.removeAttribute('disabled')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to remove 'disabled' attribute: {str(e)}"
            ) from e

    async def change_type_attribute(self, selector: str) -> None:
        """
        Changes the 'type' attribute of the specified element to 'text'.

        Args:
            selector (str): Selector of the element whose 'type' attribute will be changed.

        Raises:
            ValidationError: If the attribute cannot be changed.
        """
        try:
            await self.page.wait_for_selector(selector)
            await self.page.eval_on_selector(selector, "el => el.setAttribute('type', 'text')")
        except Exception as e:
            raise ValidationError(
                field=selector,
                message=f"Failed to change 'type' attribute to 'text': {str(e)}"
            ) from e